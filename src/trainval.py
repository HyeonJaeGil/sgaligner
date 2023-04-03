import argparse
import time

import torch.optim as optim
from engine import EpochBasedTrainer
from datasets.loaders import get_train_val_data_loader
from aligner.sg_aligner import *
from aligner.losses import *

from configs.config_scan3r_gt import make_cfg

class Trainer(EpochBasedTrainer):
    def __init__(self, cfg):
        super().__init__(cfg, max_epoch=cfg.optim.max_epoch)
        # Model Specific params
        self.modules = cfg.modules
        self.rel_dim = cfg.model.rel_dim
        self.attr_dim = cfg.model.attr_dim
        
        # Loss params
        self.zoom = cfg.loss.zoom
        self.weight_align_loss = cfg.loss.alignment_loss_weight
        self.weight_contrastive_loss = cfg.loss.constrastive_loss_weight
        
        # dataloader
        start_time = time.time()
        train_loader, val_loader = get_train_val_data_loader(cfg)
        loading_time = time.time() - start_time
        message = 'Data loader created: {:.3f}s collapsed.'.format(loading_time)
        self.logger.info(message)
        self.register_loader(train_loader, val_loader)

        # model
        model = self.create_model()
        self.register_model(model)

        # loss function and params
        loss_func_metadata = {'zoom' : self.zoom, 'wt_align_loss' : self.weight_align_loss, 
                              'wt_contrastive_loss' : self.weight_contrastive_loss, 'modules' : self.modules}
        self.loss_func = OverallLoss(ial_loss_layer = self.multi_loss_layer_ial, icl_loss_layer=self.multi_loss_layer_icl, device=self.device, metadata=loss_func_metadata)
        
        if len(self.modules) > 1:
            self.params = [{ 'params' : list(self.model.parameters()) + list(self.loss_func.align_multi_loss_layer.parameters()) + list(self.loss_func.contrastive_multi_loss_layer.parameters())}]
        else:
            self.params = [{'params' : list(self.model.parameters())}]
        
        # optimizer and scheduler
        optimizer = optim.Adam(self.params, lr=cfg.optim.lr, weight_decay=cfg.optim.weight_decay)
        self.register_optimizer(optimizer)
        scheduler = optim.lr_scheduler.StepLR(optimizer, cfg.optim.lr_decay_steps, gamma=cfg.optim.lr_decay)
        self.register_scheduler(scheduler)

        self.logger.info('Initialisation Complete')

    def create_model(self):
        model = MultiModalEncoder(modules = self.modules, rel_dim = self.rel_dim, attr_dim=self.attr_dim).to(self.device)
        
        if len(self.modules) > 1:
            self.multi_loss_layer_icl = CustomMultiLossLayer(loss_num=len(self.modules), device=self.device)
            self.multi_loss_layer_ial = CustomMultiLossLayer(loss_num=len(self.modules), device=self.device)

        message = 'Model created'
        self.logger.info(message)
        return model

    def train_step(self, epoch, iteration, data_dict):
        output_dict = self.model(data_dict)
        loss_dict = self.loss_func(output_dict, data_dict)
        # result_dict = self.evaluator(output_dict, data_dict)
        # loss_dict.update(result_dict)
        return output_dict, loss_dict

    def val_step(self, epoch, iteration, data_dict):
        output_dict = self.model(data_dict)
        loss_dict = self.loss_func(output_dict, data_dict)
        # result_dict = self.evaluator(output_dict, data_dict)
        # loss_dict.update(result_dict)
        return output_dict, loss_dict

    def set_eval_mode(self):
        self.training = False
        self.model.eval()
        self.multi_loss_layer_icl.eval()
        self.multi_loss_layer_ial.eval()
        torch.set_grad_enabled(False)

    def set_train_mode(self):
        self.training = True
        self.model.train()
        self.multi_loss_layer_ial.train()
        self.multi_loss_layer_icl.train()
        torch.set_grad_enabled(True)

def main():
    cfg = make_cfg()
    trainer = Trainer(cfg)
    trainer.run()

if __name__ == '__main__':
    main()










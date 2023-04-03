
def compute_mean_reciprocal_rank(rank_list, e1i_idxs, e2i_idxs, mrr_arr):
    for idx, e1i_idx in enumerate(e1i_idxs):
        e1_idx_rank_list = rank_list[e1i_idx]
        e1_idx_rank_list = list(e1_idx_rank_list) #.detach().cpu().numpy())
        e1_idx_rank_list.remove(e1i_idx)
        rank = e1_idx_rank_list.index(e2i_idxs[idx]) + 1
        mrr_arr.append(1.0 / rank)
    
    return mrr_arr

def compute_hits_k(rank_list, e1i_idxs, e2i_idxs, k=1):
    correct, total = 0, 0
    for idx, e1i_idx in enumerate(e1i_idxs):
        e1_idx_rank_list = rank_list[e1i_idx]
        e1_idx_rank_list = list(e1_idx_rank_list) 
        e1_idx_rank_list.remove(e1i_idx)

        e1_idx_rank_list_k = e1_idx_rank_list[:k]

        if e2i_idxs[idx] in e1_idx_rank_list_k: correct += 1
    
    total = e1i_idxs.shape[0]

    return correct, total




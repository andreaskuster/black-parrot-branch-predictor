#!/usr/bin/env python3
# encoding: utf-8

"""
    Copyright (C) 2020  Andreas Kuster

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Andreas Kuster"
__copyright__ = "Copyright 2020"
__license__ = "GPL"

import networkx as nx
import matplotlib.pyplot as plt
import pydot
import graphviz
import enum
import argparse


class Root(enum.Enum):
    FE = "fe"
    BE = "be"
    UCE = "uce"


G = nx.DiGraph()


def node_name(name, type):
    return "{}\n{}".format(type, name)


def add_nodes_recursive(name, type, hierarchy):
    for node in hierarchy[type]:
        G.add_edge(node_name(name, type), node_name(node, hierarchy[type][node]))
        add_nodes_recursive(node, hierarchy[type][node], hierarchy)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--root", default=Root.FE.name, choices=[x.name for x in Root])
    args = parser.parse_args()
    root = Root[args.root]

    _SAVE_PATH = root.value
    _ROOT = "bp_{}".format(root.value + (".v" if root == Root.UCE else "_top.v"))

    hierarchy = {
        ########
        # BP_FE
        ########
        "bp_fe_top.v": {
            "pc_gen": "bp_fe_pc_gen.v",
            "mem": "bp_fe_mem.v"
        },
        "bp_fe_mem.v": {
            "icache": "bp_fe_icache.v",
            "pma": "bp_pma.v",
            "itlb": "bp_tlb.v"
        },
        "bp_fe_pc_gen.v": {
            "shadow_priv_reg": "bsg_dff_reset_en.v",
            "shadow_translation_en_reg": "bsg_dff_reset_en.v",
            "pc_resume_reg": "bsg_dff_reset_en.v",
            "pc_gen_stage_reg": "bsg_dff_reset.v",
            "branch_metadata_fwd_reg": "bsg_dff_reset_en.v",
            "instr_scan": "bp_fe_instr_scan.v",
            "btb": "bp_fe_btb.v",
            "bp_fe_bht": "bp_fe_bht.v"
        },
        "bp_tlb.v": {
            "r_v_reg": "bsg_dff_reset.v",
            "miss_v_reg": "bsg_dff_reset.v",
            "miss_vtag_reg": "bsg_dff_reset.v",
            "plru": "bp_tlb_replacement.v",
            "vtag_cam": "bsg_cam_1r1w.v",
            "entry_ram": "bsg_mem_1rw_sync.v"
        },
        "bp_pma.v": {},
        "bp_fe_icache.v": {
            "tag_mem": "bsg_mem_1rw_sync_mask_write_bit.v",
            "data_mem": "bsg_mem_1rw_sync_mask_write_byte.v",
            "pe_load_hit": "bsg_priority_encode.v",
            "stat_mem ": "bsg_mem_1rw_sync_mask_write_bit.v",
            "lru_encoder": "bsg_lru_pseudo_tree_encode.v",
            "pe_invalid": "bsg_priority_encode.v",
            "cache_req_v_reg": "bsg_dff_reset.v",
            "cache_miss_tracker": "bsg_dff_reset_en.v",
            "data_set_select_mux": "bsg_mux.v",
            "final_data_mux": "bsg_mux.v",
            "write_mux_butterfly": "bsg_mux_butterfly.v",
            "tag_mem_way_decode": "bsg_decode.v",
            "lru_decode": "bsg_lru_pseudo_tree_decode.v",
            "read_mux_butterfly": "bsg_mux_butterfly.v",
            "cc": "bp_fe_icache_axe_trace_gen.v"
        },
        "bsg_dff_reset_en.v": {},
        "bsg_dff_reset.v": {},
        "bp_fe_instr_scan.v": {},
        "bp_fe_btb.v": {
            "tag_mem": "bsg_mem_1rw_sync.v"
        },
        "bp_fe_bht.v": {
            "r_v_reg": "bsg_dff_reset.v",
            "miss_v_reg": "bsg_dff_reset.v",
            "miss_vtag_reg": "bsg_dff_reset.v",
            "plru": "bp_tlb_replacement.v",
            "vtag_cam": "bsg_cam_1r1w.v",
            "entry_ram": "bsg_mem_1rw_sync.v"
        },
        "bsg_mem_1rw_sync_mask_write_bit.v": {
            "icg": "bsg_clkgate_optional.v",
            "synth": "bsg_mem_1rw_sync_mask_write_bit_synth.v"
        },
        "bsg_mem_1rw_sync_mask_write_byte.v": {
            "icg": "bsg_clkgate_optional.v",
            "synth": "bsg_mem_1rw_sync_mask_write_byte_synth.v"
        },
        "bsg_priority_encode.v": {
            "a": "bsg_priority_encode_one_hot_out.v",
            "b": "bsg_encode_one_hot.v"
        },
        "bsg_lru_pseudo_tree_encode.v": {
            "mux": "bsg_mux.v"
        },
        "bsg_dff_reset.v": {},
        "bsg_mux.v": {},
        "bsg_mux_butterfly.v": {
            "swap_inst": "bsg_swap.v"
        },
        "bsg_decode.v": {},
        "bsg_lru_pseudo_tree_decode.v": {},
        "bp_fe_icache_axe_trace_gen.v": {},
        "bsg_mem_1rw_sync.v": {
            "icg": "bsg_clkgate_optional.v",
            "synth": "bsg_mem_1rw_sync_synth.v"
        },
        "bsg_dff_reset.v": {},
        "bp_tlb_replacement.v": {
            "decoder": "bsg_lru_pseudo_tree_decode.v",
            "encoder": "bsg_lru_pseudo_tree_encode.v"
        },
        "bsg_cam_1r1w.v": {
            "pe": "bsg_priority_encode.v",
            "ohe": "bsg_encode_one_hot.v",
            "epe": "bsg_priority_encode.v"
        },
        "bsg_mem_1rw_sync.v": {
            "icg": "bsg_clkgate_optional.v",
            "synth": "bsg_mem_1rw_sync_synth.v"
        },
        "bsg_clkgate_optional.v": {
            "en_latch": "bsg_dlatch.v"
        },
        "bsg_mem_1rw_sync_mask_write_bit_synth.v": {
            "read_en_dff": "bsg_dff.v",
            "dff_bypass": "bsg_dff_en_bypass.v"
        },
        "bsg_mem_1rw_sync_mask_write_byte_synth.v": {
            "mem_1rw_sync": "bsg_mem_1rw_sync.v"
        },
        "bsg_priority_encode_one_hot_out.v": {
            "scan": "bsg_scan.v"
        },
        "bsg_encode_one_hot.v": {},
        "bsg_swap.v": {},
        "bsg_mem_1rw_sync_synth.v": {
            "read_en_dff": "bsg_dff.v",
            "dff_bypass": "bsg_dff_en_bypass.v"
        },
        "bsg_dlatch.v": {},
        "bsg_dff.v": {},
        "bsg_dff_en_bypass.v": {
            "dff": "bsg_dff_en.v"
        },
        "bsg_scan.v": {},
        "bsg_dff_en.v": {},
        #########
        # BP_BE
        #########
        "bp_be_top.v": {
            "be_checker": "bp_be_checker_top.v",
            "be_calculator": "bp_be_calculator_top.v",
            "be_mem": "bp_be_mem_top.v"
        },
        "bp_be_checker_top.v": {
            "director": "bp_be_director.v",
            "detector": "bp_be_detector.v",
            "scheduler": "bp_be_scheduler.v"
        },
        "bp_be_calculator_top.v": {
            "fp_bypass": "bp_be_bypass.v",
            "bypass_xrs1_mux": "bsg_mux.v",
            "bypass_xrs2_mux": "bsg_mux.v",
            "int_bypass": "bp_be_bypass.v",
            "reservation_reg": "bsg_dff.v",
            "pipe_int": "bp_be_pipe_int.v",
            "pipe_mul": "bp_be_pipe_mul.v",
            "pipe_mem": "bp_be_pipe_mem.v",
            "pipe_fp": "bp_be_pipe_fp.v",
            "calc_stage_reg": "bsg_dff.v",
            "comp_stage_mux": "bsg_mux_segmented.v",
            "comp_stage_reg": "bsg_dff.v",
            "exc_stage_reg": "bsg_dff.v"
        },
        "bp_be_mem_top.v": {
            "fault_reg": "bsg_dff_en.v",
            "vaddr_pipe": "bsg_dff_chain.v",
            "csr": "bp_be_csr.v",
            "dtlb": "bp_tlb.v",
            "pma": "bp_pma.v",
            "ptw": "bp_be_ptw.v",
            "dcache": "bp_be_dcache.v"
        },
        "bp_be_director.v": {
            "npc": "bsg_dff_reset_en.v",
            "init_mux": "bsg_mux.v",
            "exception_mux": "bsg_mux.v",
            "roll_mux": "bsg_mux.v",
            "ret_mux": "bsg_mux.v",
            "attaboy_pending_reg": "bsg_dff_reset_en.v"
        },
        "bp_be_detector.v": {},
        "bp_be_scheduler.v": {
            "issue_pkt_reg": "bsg_dff_reset_en.v",
            "issue_status_reg": "bsg_dff_reset_en.v",
            "int_regfile": "bp_be_regfile.v",
            "instr_decoder": "bp_be_instr_decoder.v"
        },
        "bp_be_bypass.v": {
            "match_one_hot_rs1": "bsg_priority_encode_one_hot_out.v",
            "match_one_hot_rs2": "bsg_priority_encode_one_hot_out.v",
            "rs1_crossbar": "bsg_crossbar_o_by_i.v",
            "rs2_crossbar": "bsg_crossbar_o_by_i.v"
        },
        "bp_be_pipe_fp.v": {},
        "bp_be_pipe_mem.v": {
            "csr_shift_reg": "bsg_shift_reg.v"
        },
        "bp_be_pipe_mul.v": {},
        "bp_be_pipe_int.v": {
            "alu": "bp_be_int_alu.v"
        },
        "bsg_mux_segmented.v": {},
        "bsg_dff_chain.v": {
            "ch_reg": "bsg_dff.v"
        },
        "bp_be_dcache.v": {
            "tag_mem": "bsg_mem_1rw_sync_mask_write_bit.v",
            "data_mem": "bsg_mem_1rw_sync_mask_write_byte.v",
            "pe_load_hit": "bsg_priority_encode.v",
            "pe_store_hit": "bsg_priority_encode.v",
            "wbuf": "bp_be_dcache_wbuf.v",
            "stat_mem": "bsg_mem_1rw_sync_mask_write_bit.v",
            "lru_encoder": "bsg_lru_pseudo_tree_encode.v",
            "pe_invalid": "bsg_priority_encode.v",
            "cache_req_v_reg": "bsg_dff_reset.v",
            "cache_miss_tracker": "bsg_dff_reset_en.v",
            "cache_miss_detect": "bsg_edge_detect.v",
            "lock_counter": "bsg_counter_clear_up.v",
            "ld_data_set_select_mux": "bsg_mux.v",
            "bypass_mux_segmented": "bsg_mux_segmented.v",
            "final_data_mux": "bsg_mux.v",
            "word_mux": "bsg_mux.v",
            "half_mux": "bsg_mux.v",
            "byte_mux": "bsg_mux.v",
            "wbuf_data_mem_v_decode ": "bsg_decode.v",
            "write_mux_butterfly": "bsg_mux_butterfly.v",
            "lce_tag_mem_way_decode": "bsg_decode.v",
            "lru_decode": "bsg_lru_pseudo_tree_decode.v",
            "dirty_mask_decode": "bsg_decode_with_v.v",
            "read_mux_butterfly": "bsg_mux_butterfly.v",
            "axe_trace_gen": "bp_be_dcache_axe_trace_gen.v"
        },
        "bp_be_ptw.v": {
            "dcache_data_reg": "bsg_dff_reset.v",
            "vpn_reg": "bsg_dff_reset_en.v",
            "ppn_reg": "bsg_dff_reset_en.v",
            "tlb_sel_reg": "bsg_dff_reset_en.v",
            "cmd_sel_reg": "bsg_dff_reset_en.v"
        },
        "bp_pma.v": {},
        "bp_be_csr.v": {
            "mcause_exception_enc": "bsg_priority_encode.v",
            "m_interrupt_enc": "bsg_priority_encode.v",
            "s_interrupt_enc": "bsg_priority_encode.v",
            "debug_mode_reg": "bsg_dff_reset.v",
            "priv_mode_reg": "bsg_dff_reset.v",
            "translation_en_reg": "bsg_dff_reset.v"
        },
        "bp_be_instr_decoder.v": {},
        "bp_be_regfile.v": {
            "rf": "bsg_mem_2r1w_sync.v",
            "rs_addr_reg": "bsg_dff_reset_en.v",
            "rw_fwd_reg": "bsg_dff.v"
        },
        "bsg_crossbar_o_by_i.v": {
            "mux_one_hot": "bsg_mux_one_hot.v"
        },
        "bsg_shift_reg.v": {},
        "bp_be_int_alu.v": {},
        "bp_be_dcache_wbuf.v": {
            "mux_segmented_merge0": "bsg_mux_segmented.v",
            "mux_segmented_merge1": "bsg_mux_segmented.v"
        },
        "bsg_edge_detect.v": {},
        "bsg_counter_clear_up.v": {},
        "bsg_decode_with_v.v": {
            "bd": "bsg_decode.v"
        },
        "bp_be_dcache_axe_trace_gen.v": {},
        "bsg_mem_2r1w_sync.v": {
            "icg": "bsg_clkgate_optional.v",
            "synth": "bsg_mem_2r1w_sync_synth.v"
        },
        "bsg_mem_2r1w_sync_synth.v": {},
        "bsg_mux_one_hot.v": {},
        #########
        # BP_UCE
        #########
        "bp_uce.v": {
            "cache_req_reg": "bsg_dff_reset_en.v",
            "metadata_reg": "bsg_dff_en_bypass.v",
            "metadata_v_reg": "bsg_dff_en_bypass.v",
            "dirty_data_reg": "bsg_dff_en_bypass.v",
            "dirty_tag_reg": "bsg_dff_en_bypass.v",
            "index_counter": "bsg_counter_set_down.v"
        },
        "bsg_counter_set_down.v": {}
    }


    add_nodes_recursive("root", _ROOT, hierarchy)


    print(G.adj)

    # some point (for large graphs)
    plt.axis('off')
    # generate positions
    positions = nx.nx_pydot.graphviz_layout(G, prog="dot", )
    if root == Root.UCE:
        plt.figure(figsize=(15, 5))
    elif root == Root.FE:
        plt.figure(figsize=(64, 16))
    elif root == Root.BE:
        plt.figure(figsize=(80, 16))

    nx.draw_networkx_nodes(G=G, pos=positions)
    nx.draw_networkx(G=G, pos=positions, node_size=1000, font_size=6)

    # save plot to file if save_path has been specified
    if _SAVE_PATH is not None:
        plt.savefig(_SAVE_PATH)
    # plot it
    plt.show()
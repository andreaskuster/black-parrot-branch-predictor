/*
 * bp_fe_bp_perceptron.v
*/
module bp_fe_bp_perceptron
  #( parameter bht_idx_width_p          = "inv"
   , parameter bp_n_hist                = "inv"
  )
  ( input                       clk_i
  , input                       reset_i

  , input                       w_v_i
  , input [bht_idx_width_p-1:0] idx_w_i
  , input                       correct_i

  , input                       r_v_i
  , input [bht_idx_width_p-1:0] idx_r_i
  , output                      predict_o
  );

// TODO

`ifndef VERILATOR
  // dump waves
  initial begin
    $dumpfile("dump.vcd");
  end
`endif

endmodule

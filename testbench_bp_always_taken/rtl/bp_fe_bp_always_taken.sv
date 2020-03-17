/*
 * bp_fe_bp_always_taken.v
 *
 *  Copyright (C) 2020  Andreas Kuster
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
*/
module bp_fe_bp_always_taken
  ( 
  , input  r_v_i
  , output predict_o
  );

  // always predict 'taken'
  assign predict_o = r_v_i ? 1'b1 : 1'b0;

endmodule

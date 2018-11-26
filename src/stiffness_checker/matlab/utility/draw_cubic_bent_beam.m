function [D_global] = draw_cubic_bent_beam(end_u, end_v, end_u_D, end_v_D, exagg)
% Computes cubic deflection functions from end deflections
% and end rotations. These bent shapes are exact for mode-shapes, 
% and for frames loaded at their nodes.
% Input
% end_u = 1x(dim) node coordinate, dim = 2 or 3
% end_v = 1x(dim) ..
% end_u_D = 1 x (full_node_dof) deformation
%   [x,y,z,theta1,theta2,theta3]
% exagg = exaggeration factor

assert(all(size(end_u_D) == size(end_v_D)));
assert(all(size(end_u) == size(end_v)));

full_node_dof = size(end_u_D,2);
assert(full_node_dof==3 || full_node_dof==6);
dim = size(end_u,2);
assert(dim==2 || dim==3);

L = norm(end_u - end_v);
R_b = local_frame(end_u, end_v, 0);

R = zeros(full_node_dof*2, full_node_dof*2);
for k=1:1:(full_node_dof/3)*2
    R(k*3-3+1:k*3,...
      k*3-3+1:k*3) = R_b;
end

% compute end deflections in local coordinates
D_global = [end_u_D'; end_v_D'];
D_local = exagg*R*D_global;

% curve-fitting problem for a cubic polynomial
x_l_u = D_local(1);
x_l_v = D_local(4) + L;

A_m = [[1, x_l_u, x_l_u^2, x_l_u^3];...
       [1, x_l_v, x_l_v^2, x_l_v^3];...
       [0, 1,     2*x_l_u, 3*x_l_u^2];...
       [0, 1,     2*x_l_v, 3*x_l_v^2]];
a_coeff = A_m\D_local([2,5,3,6],:);

if full_node_dof == 6
   b_coeff = A_m\D_local([2,5,3,6],:);
end

disc = 10;
D_global = zeros(disc+1, dim) ;

for i=0:1:disc
    s = D_local(1) + i*abs(L+D_local(4)-D_local(1))/disc;
    if s > 1.01*abs(L+D_local(4))
        break
    end
    
    v = a_coeff'*[1;s;s^2;s^3];
    dD_global = R(1:2,1:2)\[s;v];
    D_global(i+1,:) = end_u + dD_global';
end

% check nodal displacement agreement
% o_d = [end_u_D'; end_v_D'];
% o_d([1,2,4,5]) + [end_u'; end_v']

end
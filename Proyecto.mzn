% Parameters
int: n;  % number of people
int: m;  % number of possible opinions
array[1..m] of int: pi;  % initial distribution of opinions
array[1..m] of float: vi;  % values of opinions
array[1..m] of float: cei;  % extra costs for opinions
array[1..m,1..m] of float: ci;  % cost matrix for opinion changes
float: ct;  % maximum total cost allowed
int: maxM;  % maximum number of movements allowed

% Decision Variables
array[1..m,1..m] of var 0..n: x;  % number of people moving from opinion i to j

% Auxiliary Variables for final distribution
array[1..m] of var 0..n: final_dist;  % final distribution after movements

% Calculate final distribution
constraint forall(j in 1..m)(
  final_dist[j] = pi[j] - sum(i in 1..m)(x[j,i]) + sum(i in 1..m)(x[i,j])
);

int: max_possible_moves = min(n, maxM);
constraint forall(i,j in 1..m)(
    x[i,j] <= min(pi[i], max_possible_moves)
);

constraint forall(i in 1..m)(x[i,i] = 0);

% Constraint: Total people remains constant
constraint sum(i in 1..m)(final_dist[i]) = n;

% Optimization: Add bounds for final distribution
constraint forall(j in 1..m)(
    final_dist[j] <= n
);

% Constraint: Movement cost calculation and limit
var float: total_cost = sum(i,j in 1..m where i != j)(
  let {
    var float: base_cost = ci[i,j] * (1.0 + pi[i]/n);
  } in
  if pi[j] > 0 then
    base_cost * x[i,j]
  else
    (base_cost + cei[j]) * x[i,j]
  endif
);
constraint total_cost <= ct;

% Constraint: Maximum movements calculation
constraint sum(i,j in 1..m where i != j)(abs(j-i) * x[i,j]) <= maxM;


array[1..m] of float: sorted_vi = sort(vi);

% Función para encontrar la mediana basada en la distribución de personas
function var float: find_population_median(array[int] of var int: dist, array[int] of float: values) =
    let {
        % Total de personas
        var int: total = sum(dist),
        % Posición mediana en la población total
        var float: median_pos = total / 2.0
    } in
    % La mediana es el valor de la opinión donde la suma acumulada de personas supera la mitad
    let {
        array[1..m+1] of var int: cum_sum = [0] ++ [ sum(i in 1..j)(dist[i]) | j in 1..m ]
    } in
    let {
        var int: median_idx = min([ i | i in 1..m where cum_sum[i+1] >= ceil(median_pos) ])
    } in
    values[median_idx];

% Calcular la polarización usando la mediana basada en la población
var float: population_median = find_population_median(final_dist, vi);
var float: polarization = sum(i in 1..m)(
    final_dist[i] * abs(vi[i] - population_median)
);


% Calculate total movements between opinions
var int: total_movements = sum(i,j in 1..m where i != j)(x[i,j]);

% Search annotation to guide solver
ann: search_strategy = int_search(
    [x[i,j] | i,j in 1..m where i != j], 
    first_fail,  % Choose variables with smallest domain first
    indomain_min,  % Try smaller values first
    complete  % Complete search
);

% Objective: Minimize polarization
solve :: search_strategy minimize polarization;

% Output
output [
    "Polarization: \(polarization)\n",
    "Final distribution: \(final_dist)\n",
    "Movements matrix:\n"] ++
    [if j = 1 then "\n" else " " endif ++ show(x[i,j]) | i,j in 1..m] ++
    ["\nTotal cost: \(total_cost)\n",
    "Total movements between opinions: \(total_movements)\n"
];
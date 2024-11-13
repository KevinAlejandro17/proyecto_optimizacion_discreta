% Parámetros
int: n;                       % Número total de personas
int: m;                       % Número de opiniones posibles
array[1..m] of int: pi;       % Distribución inicial de personas por opinión
array[1..m] of float: vi;     % Valor de cada opinión
array[1..m] of float: cei;    % Costo extra si una opinión inicialmente no tenía personas
array[1..m, 1..m] of float: ci; % Costos de mover personas de una opinión a otra
float: ct;                    % Costo total máximo permitido
int: maxM;                    % Número máximo de movimientos permitidos

array[1..m, 1..m] of var 0..n: x; % Número de personas movidas de opinión i a j

array[1..m] of var 0..n: final_dist; % Distribución final después de los movimientos

constraint forall(j in 1..m) (
    final_dist[j] = pi[j] - sum(k in 1..m)(x[j,k]) + sum(k in 1..m)(x[k,j])
);

constraint sum(j in 1..m)(final_dist[j]) = n;

constraint forall(i in 1..m) (
    sum(j in 1..m)(x[i,j]) <= pi[i]
);

constraint sum(i,j in 1..m where i != j)(
    ci[i,j] * x[i,j] * (1 + pi[i]/n) + 
    if pi[j] = 0 then cei[j] * x[i,j] else 0 endif
) <= ct;

constraint sum(i,j in 1..m where i != j)(abs(j-i) * x[i,j]) <= maxM;

% Función para calcular la mediana de la distribución final
function var float: calc_median(array[1..m] of var int: dist, array[1..m] of float: vals) =
    let {
        var float: median = sum(i in 1..m)(dist[i] * vals[i]) / n;
    } in median;

% Función objetivo: minimizar la polarización
var float: median = calc_median(final_dist, vi);
var float: polarization = sum(i in 1..m)(final_dist[i] * abs(vi[i] - median));

solve minimize polarization;


var float: initial_polarization = sum(i in 1..m)(pi[i] * abs(vi[i] - median));

/*
output [
    "Polarización mínima alcanzada: ", show(polarization), "\n",
    "Distribución final: ", show(final_dist), "\n",
    "Mediana: ", show(median), "\n",
    "Movimientos:\n", show(x), "\n",
    "Costo total: ", show(sum(i,j in 1..m where i != j)(
        ci[i,j] * x[i,j] * (1 + pi[i]/n) + 
        if pi[j] = 0 then cei[j] * x[i,j] else 0 endif
    ))
];
*/

output [
    "Polarización inicial: ", show(initial_polarization), "\n",
    "Polarización mínima alcanzada: ", show(polarization), "\n",
    "Distribución inicial: ", show(pi), "\n",
    "Distribución final: ", show(final_dist), "\n",
    "Mediana: ", show(median), "\n",
    "Número total de movimientos: ", show(sum(i,j in 1..m where i != j)(x[i,j])), "\n",
    "Costo total: ", show(sum(i,j in 1..m where i != j)(
        ci[i,j] * x[i,j] * (1 + pi[i]/n) + 
        if pi[j] = 0 then cei[j] * x[i,j] else 0 endif
    ))
];
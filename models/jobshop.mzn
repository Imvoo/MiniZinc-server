% The job-shop scheduling problem.
% --------------------------------
%
% A job shop has some machines, each performing a different operation.
% There are some jobs to be performed.
% A job is a sequence of tasks.
% A task involves processing by a single machine for some duration.
% A machine can operate on at most one task at a time.
% Tasks cannot be interrupted.xr
%
% The goal is to schedule each job to minimise the finishing time.
%

% Model parameters.
%

int: n_machines;                        % The number of machines.
int: n_jobs;                            % The number of jobs.
int: n_tasks_per_job = n_machines;      % Each job has one task per machine.

set of int: jobs = 1..n_jobs;
set of int: tasks = 1..n_tasks_per_job;
set of int: machines = 0..n_machines-1;

    % job_task_machine[j, k] is the machine required by task k of job j.
array [jobs, tasks] of int: job_task_machine;

    % job_task_duration[j, k] is the duration of task k of job j.
array [jobs, tasks] of int: job_task_duration;

%-----------------------------------------------------------------------------%
% Model variables.
%

    % The start time of each job task.
array [jobs, tasks] of var 0..infinity: job_task_start;

    % The finishing time is the time of the last task to complete.
var int: t_end;

% array[int,int] of var int: machine_task_start =
% array2d(machines,tasks, [ job_task_start[j,t] | m in machines, j in jobs, t in tasks where job_task_machine[j,t]=m ]);

% array[int,int] of var int: machine_task_duration =
% array2d(machines,tasks, [ job_task_duration[j,t] | m in machines, j in jobs, t in tasks where job_task_machine[j,t]=m ]);

% constraint trace(show(machine_task_duration));

% array [machines, tasks, tasks] of var bool: precedes;

% constraint forall (m in machines) (
%   forall (t1,t2 in tasks where t1<t2) (
%       ( precedes[m,t1,t2] -> machine_task_start[m,t1]+machine_task_duration[m,t1] <= machine_task_start[m,t2] )
%   /\  ( precedes[m,t1,t2] \/ machine_task_start[m,t2]+machine_task_duration[m,t2] <= machine_task_start[m,t1] )
%   )
% /\
%   forall (t1,t2 in tasks where t1>=t2) (precedes[m,t1,t2])
% );

%-----------------------------------------------------------------------------%
% Constraints.
%

    % Each job task must complete before the next.
    %

constraint
    forall ( j in jobs, k in 1..(n_tasks_per_job - 1) ) (
        job_task_start[j, k] + job_task_duration[j, k]  <=
            job_task_start[j, k + 1]
    );

constraint
    forall ( j in jobs ) (
        0  <=  job_task_start[j, 1]
    );

    % Tasks on the same machine cannot overlap.
    %
constraint
    forall (
        ja in jobs,
        jb in (ja + 1)..n_jobs,
        ka, kb in tasks
    ) (
        if
           job_task_machine[ja, ka]  =  job_task_machine[jb, kb]
        then
            no_overlap(
                job_task_start[ja, ka], job_task_duration[ja, ka],
                job_task_start[jb, kb], job_task_duration[jb, kb]
            )
        else
            true
        endif
    );

include "globals.mzn";

%constraint forall (m in 0..n_machines-1) (
%  cumulative(
%  [job_task_start[i,j] | i in jobs, j in tasks where job_task_machine[i,j]=m],
%  [job_task_duration[i,j] | i in jobs, j in tasks where job_task_machine[i,j]=m],
%  [1 | i in jobs, j in tasks where job_task_machine[i,j]=m],
%  1
%  )
%);

predicate no_overlap(var int: t_a, var int: d_a, var int: t_b, var int: d_b)  =
    ( t_a + d_a  <=  t_b )  \/  ( t_b + d_b  <=  t_a );

    % The finishing time must be no earlier than the finishing time
    % of any task.
    %
constraint
    forall ( j in jobs ) (
            job_task_start[j, n_tasks_per_job] +
            job_task_duration[j, n_tasks_per_job]
        <=
            t_end
    );


%-----------------------------------------------------------------------------%
% Objective.
%

%include "gecode.mzn";

solve
% ::relax_and_reconstruct(array1d(precedes),90)
 ::int_search(array1d(job_task_start), input_order, indomain_min, complete)
%  ::seq_search([bool_search(array1d(precedes),dom_w_deg,indomain_max,complete),
%                int_assign(array1d(job_task_start), indomain_min)])
minimize t_end;

% include "../viz/jobshop.mzn";
% include "../viz/objective.mzn";
%
% output [viz_jobshop(job_task_start, job_task_duration, job_task_machine),"%%%bottom"++viz_objective(t_end)];

%output [show(t_end)];

%-----------------------------------------------------------------------------%
%-----------------------------------------------------------------------------%

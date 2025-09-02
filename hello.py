from dataclasses import dataclass

from ortools.sat.python import cp_model

model = cp_model.CpModel()


@dataclass
class Task:
    name: str
    duration1: int
    wait: int
    duration2: int
    start1: cp_model.IntVar | None = None
    end1: cp_model.IntVar | None = None
    start2: cp_model.IntVar | None = None
    end2: cp_model.IntVar | None = None
    interval1: cp_model.IntervalVar | None = None
    interval2: cp_model.IntervalVar | None = None

    def sum_time(self) -> int:
        return self.duration1 + self.wait + self.duration2


# 各タスク
tasks = [
    Task("A", 3, 2, 2),
    Task("B", 2, 5, 4),
    Task("C", 7, 4, 1),
]


max_time = sum(task.sum_time() for task in tasks)
for task in tasks:
    # タスクの開始時刻、終了時刻
    start1 = model.NewIntVar(0, max_time, f"start1_{task.name}")
    end1 = model.NewIntVar(0, max_time, f"end1_{task.name}")
    model.Add(end1 == start1 + task.duration1)
    start2 = model.NewIntVar(0, max_time, f"start2_{task.name}")
    end2 = model.NewIntVar(0, max_time, f"end2_{task.name}")
    model.Add(end2 == start2 + task.duration2)
    model.Add(start2 == end1 + task.wait)
    # リソース競合、タスクが重ならないようにする
    interval1 = model.NewIntervalVar(
        start1, task.duration1, end1, f"interval1_{task.name}"
    )
    interval2 = model.NewIntervalVar(
        start2, task.duration2, end2, f"interval2_{task.name}"
    )
    task.start1 = start1
    task.end1 = end1
    task.start2 = start2
    task.end2 = end2
    task.interval1 = interval1
    task.interval2 = interval2

# リソース競合
intervals_ = [task.interval1 for task in tasks] + [task.interval2 for task in tasks]
intervals = [interval for interval in intervals_ if interval is not None]
model.AddNoOverlap(intervals)

# 目的関数: makespan 最小化
makespan = model.NewIntVar(0, max_time, "makespan")
for task in tasks:
    model.Add(task.end2 <= makespan)
model.Minimize(makespan)

solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Objective value =", solver.ObjectiveValue())
    for task in tasks:
        if (
            task.start1 is not None
            and task.end1 is not None
            and task.start2 is not None
            and task.end2 is not None
        ):
            print(
                f"{task.name}: {solver.Value(task.start1)} - {solver.Value(task.end1)}"
                f", {solver.Value(task.start2)} - {solver.Value(task.end2)}"
            )
else:
    print("No solution found.")

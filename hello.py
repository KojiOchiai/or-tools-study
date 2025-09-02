from ortools.sat.python import cp_model

model = cp_model.CpModel()

# 各タスク
tasks = {
    "job1": {"duration": 3, "consumption": 2},
    "job2": {"duration": 2, "consumption": 1},
    "job3": {"duration": 4, "consumption": 3},
}


# タスク開始時間変数
start_ver = []
end_ver = []
intervals = []

for name, info in tasks.items():
    # タスクの開始時刻、終了時刻
    start = model.NewIntVar(0, 10, f"start_{name}")
    end = model.NewIntVar(0, 10, f"end_{name}")
    model.Add(end == start + info["duration"])
    # リソース競合、タスクが重ならないようにする
    interval = model.NewIntervalVar(start, info["duration"], end, f"interval_{name}")
    start_ver.append(start)
    end_ver.append(end)
    intervals.append(interval)

# リソース競合
model.AddNoOverlap(intervals)

# 目的関数: makespan 最小化
makespan = model.NewIntVar(0, 20, "makespan")
for end in end_ver:
    model.Add(end <= makespan)
model.Minimize(makespan)

solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Objective value =", solver.ObjectiveValue())
    for start, end in zip(start_ver, end_ver):
        print(f"start_{start}: {solver.Value(start)} - {solver.Value(end)}")
else:
    print("No solution found.")

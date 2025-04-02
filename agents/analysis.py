import polars as pl
import json
import os
import re
import matplotlib.pyplot as plt
import seaborn as sns

os.makedirs("results/charts", exist_ok=True)

# ---------- Log Parsing ----------
completion_pattern = r'"completion_tokens":\s*(\d+)|'
prompt_pattern = r'"prompt_tokens":\s*(\d+)|'
total_pattern = r'"total_tokens":\s*(\d+)'

log_files = os.listdir("results/logs")
meta_data_list = [
    {
        "trial": int(log_file.split(".")[0].split("_")[-1]),
        "agent": "_".join(log_file.split(".")[0].split("_")[0:-1]),
        "file_path": log_file,
    }
    for log_file in log_files
]

# Itterate over files
for meta_data in meta_data_list:
    file_path = meta_data["file_path"]

    with open(f"results/logs/{file_path}", "r") as file:
        steps = json.load(file)

        duration = 0
        completion_tokens = 0
        prompt_tokens = 0
        total_tokens = 0

        # Itterate over steps in file
        for step in steps[1:]:
            duration += step["end_time"] - step["start_time"]

            text = step["model_output_message"]

            completion_pattern = r'"completion_tokens":\s*(\d+)'
            prompt_pattern = r'"prompt_tokens":\s*(\d+)'
            total_pattern = r'"total_tokens":\s*(\d+)'

            completion_tokens += int(re.search(completion_pattern, text).group(1))
            prompt_tokens += int(re.search(prompt_pattern, text).group(1))
            total_tokens += int(re.search(total_pattern, text).group(1))

        meta_data["duration"] = duration
        meta_data["completion_tokens"] = completion_tokens
        meta_data["prompt_tokens"] = prompt_tokens
        meta_data["total_tokens"] = total_tokens

meta_data_df = pl.from_dicts(meta_data_list)

# ---------- Results Aggregation ----------

true_values = pl.from_dicts(
    [
        {"task": "sales_growth_rate", "true_value": 0.2202},
        {"task": "sales", "true_value": 113.51},
        {"task": "cost_of_goods_sold", "true_value": 72.80},
    ]
)

agent_task_df = (
    pl.read_csv("results/*.csv")
    .join(true_values, on=["task"], how="left")
    .with_columns(
        pl.when(pl.col("task").eq("sales_growth_rate"))
        .then(pl.col("predicted_value").round(4))
        .otherwise(pl.col("predicted_value").round(2))
    )
    .with_columns(
        pl.col("true_value").eq(pl.col("predicted_value")).alias("correct"),
    )
    .join(meta_data_df, on=["trial", "agent"], how="left")
    .group_by(["agent", "task"])
    .agg(
        pl.col("completion_tokens").mean(),
        pl.col("prompt_tokens").mean(),
        pl.col("total_tokens").mean(),
        pl.col("duration").mean(),
        pl.col("steps").mean(),
        pl.col("error").mean(),
        pl.col("correct").mul(100).alias("accuracy").mean(),
    )
    .with_columns(
        pl.col("completion_tokens", "prompt_tokens", "total_tokens").cast(pl.Int32)
    )
    .sort(["agent", "task"])
)

print(agent_task_df)

agent_df = agent_task_df.group_by("agent").agg(
    pl.col("completion_tokens").sum(),
    pl.col("prompt_tokens").sum(),
    pl.col("total_tokens").sum(),
    pl.col("duration").sum(),
    pl.col("steps").sum(),
    pl.col("error").mean(),
    pl.col("accuracy").mean(),
)

print(agent_df)


# ---------- Token Usage Plot ----------

fig, ax = plt.subplots(figsize=(9, 6))

ax.bar(agent_df["agent"], agent_df["prompt_tokens"], label="Prompt Tokens")
ax.bar(
    agent_df["agent"],
    agent_df["completion_tokens"],
    bottom=agent_df["prompt_tokens"],
    label="Completion Tokens",
)

plt.ylabel("Token Count")
plt.xlabel("Agent")
plt.title("Stacked Token Usage by Agent")
plt.legend()

plt.savefig("results/charts/token_usage.png", dpi=300)


# ---------- Time Duration Plot ----------

fig, ax = plt.subplots(figsize=(9, 6))

sns.barplot(agent_df, x="agent", y="duration")

plt.ylabel("Duration (s)")
plt.xlabel("Agent")
plt.title("Time Duration by Agent")

plt.savefig("results/charts/time_duration.png", dpi=300)

# ---------- Steps Plot ----------

fig, ax = plt.subplots(figsize=(9, 6))

sns.barplot(agent_task_df, x="agent", y="steps", hue="task")

plt.ylabel("Steps")
plt.xlabel("Agent")
plt.title("Agent Steps by Task")

plt.savefig("results/charts/steps.png", dpi=300)

# ---------- Accuracy Plot ----------

fig, ax = plt.subplots(figsize=(9, 6))

sns.barplot(agent_task_df, x="agent", y="accuracy", hue="task")

plt.ylabel("Accuracy (%)")
plt.xlabel("Agent")
plt.title("Agent Accuracy by Task")

plt.legend(title="Task", bbox_to_anchor=(1, 1), loc="upper left")

plt.tight_layout()

plt.savefig("results/charts/accuracy.png", dpi=300)

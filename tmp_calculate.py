import statistics

# 示例列表
a = [9.35, 9.33, 10.44]

# 计算均值
mean = statistics.mean(a)

# 计算标准差
std_dev = statistics.stdev(a)

# 输出结果
print(f"{round(mean, 2)} ± {round(std_dev, 2)}")
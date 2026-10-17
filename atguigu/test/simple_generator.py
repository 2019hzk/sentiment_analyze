async def simple_generator():
    print("  [生成器内部] 1. 开始执行，准备吐出第一条数据...")
    yield "数据 A"  # 程序在这里暂停！把 "数据 A" 交出去

    print("  [生成器内部] 2. 恢复执行，准备吐出第二条数据...")
    yield "数据 B"  # 再次暂停！把 "数据 B" 交出去

    print("  [生成器内部] 3. 彻底执行完毕！")


# 1. 调用函数时，里面一行代码都不会执行，只是拿到了一个“生成器对象”
gen = simple_generator()
print(f"调用函数返回的是: {gen}\n")

# # 2. 用 for 循环去驱动它（就像 EventSourceResponse 在背后做的那样）
for item in gen:
    print(f"外部消费者 收到了: {item}\n")
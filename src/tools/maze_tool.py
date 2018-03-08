#coding:utf-8
#Created by weimi on 2018/3/8.

# 随机生成迷宫
def random_maze(n, m, max_height=0):
    import random
    maze = []
    # 记录 格子 所在的区域 标记 初始为自己
    grid_map_key = {}
    global_map = {}
    for i in range(n):
        arr = []
        for j in range(m):
            # (向右的墙壁, 向下的墙壁, 格子高度) 0 为不通
            arr.append([0, 0, random.randint(0, max_height)])
            num = i * m + j
            global_map[num] = [num]
            grid_map_key[num] = num

        maze.append(arr)
    # return maze
    # 1.随机 打通 向右的墙壁(不通才随机打通), 将连通的 格子合并
    # 2.随机 从每个连通的区域 选择 >=1 个格子打通向下的墙壁
    # 3.将最后一行的 所有非连通块打通

    for i in range(n):
        # 当前行的连通区
        line_map = {}
        for j in range(m):
            # 当前格子
            grid1 = i * m + j

            if grid_map_key[grid1] not in line_map:
                line_map[grid_map_key[grid1]] = [grid1]
            elif grid1 not in line_map[grid_map_key[grid1]]:
                line_map[grid_map_key[grid1]].append(grid1)

            if j == m - 1:
                continue
            # 右边 格子
            grid2 = grid1 + 1

            # 在同一连通块
            if grid_map_key[grid1] == grid_map_key[grid2]:
                continue
            # 随机 向右 打通 最后一行所有未连通块 打通
            if i == n - 1 or random.randint(0, 2) % 2 == 0:
                maze[i][j][0] = 1
                key1 = grid_map_key[grid1]

                map1 = global_map[key1]

                key2 = grid_map_key[grid2]

                # 将两块连通区合并
                for grid in global_map[key2]:
                    grid_map_key[grid] = key1
                    map1.append(grid)

                del global_map[key2]

                # 将打通的两个格子所在的当前行连通区 合并
                if key2 not in line_map:
                    line_map[key2] = [grid2]

                for grid in line_map[key2]:
                    line_map[key1].append(grid)

                del line_map[key2]

        if i != n - 1:
            for key in line_map.keys():
                grid_list = line_map[key]
                idx1 = random.randint(0, len(grid_list) - 1)

                grid_idx_list = [idx1]

                for idx in range(len(grid_list)):
                    if idx != idx1 and random.randint(1, 2) % 2 == 0:
                        grid_idx_list.append(idx)

                for idx in grid_idx_list:
                    grid1 = grid_list[idx]
                    x = grid1 // m
                    y = grid1 % m
                    maze[x][y][1] = 1

                    grid2 = (x + 1) * m + y
                    key1 = grid_map_key[grid1]
                    key2 = grid_map_key[grid2]
                    grid_map_key[grid2] = key1
                    global_map[key1].append(grid2)
                    del global_map[key2]

    return maze


def print_maze(maze, print_height=False):
    n = len(maze)
    m = len(maze[0])

    def num_to_ch(num):
        return chr(65 + num)

    for j in range(m):
        if j == 0:
            print('    ', end='')
        print('%s   ' % num_to_ch(j), end='')
    print("")
    for i in range(n):
        # 打印上面墙壁
        for j in range(m):

            if j == 0:
                print('  ', end='')
                print('x ', end='')
            if maze[i - 1][j][1] == 1:
                print("  ", end='')
            else:
                print("x ", end='')
            print('x ', end='')
        print("")
        # 打印左边墙壁
        for j in range(m + 1):
            if j == 0 or j == m:
                if j == 0:
                    print('%s ' % num_to_ch(i), end='')
                print("x ", end='')
            else:
                if maze[i][j-1][0] == 1:
                    print("  ", end='')
                else:
                    print("x ", end='')
            if print_height:
                if j < m:
                    print("%d " % (maze[i][j][2]), end="")
                else:
                    print("  ", end="")
            else:
                print("  ", end="")
        print("")
    for j in range(m):
        if j == 0:
            print('  ', end='')
            print('x ', end='')
        print("x x ", end='')
    print("")

maze = random_maze(20, 20, max_height=0)

print_maze(maze, print_height=False)


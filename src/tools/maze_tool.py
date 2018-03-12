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

# 打印迷宫
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

class State(object):

    dx = (1, 0, -1, 0)
    dy = (0, 1, 0, -1)

    def __init__(self, x, y, direction, path):
        self.x = x
        self.y = y
        self.path = path
        self.direction = direction
        self.step = len(path)
        return

    # opt 0 向前, 1 左转 -1 右转
    def transform(self, opt, maze):
        if opt == 0:
            flag, data = self._move(maze=maze)
            if not flag:
                return False
            self.x, self.y = data
        elif opt in [-1, 1]:
            self.direction = (4 + self.direction + opt) % 4
        else:
            raise ValueError('opt error')
        self.path.append(opt)
        self.step += 1
        return True

    def _move(self, maze):
        x2 = self.x + State.dx[self.direction]
        y2 = self.y + State.dy[self.direction]
        n = len(maze)
        m = len(maze[0])

        if x2 < 0 or y2 < 0 or x2 >= n or y2 >= m:
            return False, '越界'

        # (向右的墙壁, 向下的墙壁, 格子高度) 0 为不通
        grid1 = maze[self.x][self.y]
        grid2 = maze[x2][y2]

        grid = grid1
        if self.direction >= 2:
            grid = grid2
        idx = 1 - self.direction % 2
        if grid[idx] == 1:
            return True, (x2, y2)
        return False, '墙壁'


    def __lt__(self, other):
        return self.step < other.step

def start_state():
    return State(**{
        'x': 0,
        'y': 0,
        'direction': 0,
        'path': [],
    })

# 遍历迷宫最短路径
def bfs_maze(maze):
    n = len(maze)
    m = len(maze[0])

    end_x = n - 1
    end_y = m - 1

    maze_min_step = []
    for i in range(n):
        arr = []
        for j in range(m):
            arr.append({})
        maze_min_step.append(arr)

    from queue import PriorityQueue
    q = PriorityQueue()
    q.put_nowait(start_state())
    import copy
    while not q.empty():
        s = q.get_nowait()
        if s.x == end_x and s.y == end_y:
            return True, s.path
        for opt in [0, 1, -1]:
            ss = State(**{
                'x': s.x,
                'y': s.y,
                'direction': s.direction,
                'path': copy.deepcopy(s.path),
            })
            flag = ss.transform(opt=opt, maze=maze)
            if not flag:
                continue
            x = ss.x
            y = ss.y
            if ss.direction in maze_min_step[x][y] and maze_min_step[x][y][ss.direction] <= ss.step:
                continue
            maze_min_step[x][y][ss.direction] = ss.step
            q.put_nowait(ss)
    return False, '不可达'

def _get_block(block_id, block_list):
    if block_id < 0 or block_id >= len(block_list):
        raise ValueError('模块%d未找到!' % block_id)
    return block_list[block_id]

def _dfs_path(path, block_list, block_dict, p_block_id=None):
    for opt in path:
        if isinstance(opt, int):
            if opt not in [-1, 0, 1]:
                raise ValueError('路径非法')
        elif isinstance(opt, dict):
            if 'id' not in opt:
                raise ValueError('路径非法')
            block_id = opt['id']
            if block_id not in block_dict:
                block_dict[block_id] = 0
            block_dict[block_id] = block_dict[block_id] + 1
            block = _get_block(block_id=block_id, block_list=block_list)
            if p_block_id == block_id:
                raise ValueError('模块内不能包含自身!')
            _dfs_path(path=block, block_list=block_list, block_dict=block_dict, p_block_id=block_id)
        else:
            raise ValueError('路径非法')

# 返回 步数
def run_block(state, block_id, block_list, block_dict, maze, global_grid_count):
    block = _get_block(block_id=block_id, block_list=block_list)
    step = 0
    i = 1
    if block_dict[block_id] > 1:
        i = 0
        step = 1
    for opt in block:
        if isinstance(opt, int):
            flag = state.transform(opt=opt, maze=maze)
            if not flag:
                return -1
            flag, count = check_grid_count(state=state, global_grid_count=global_grid_count)
            if not flag:
                return -1
            step += i
        else:
            step_tmp = run_block(state=state, block_id=opt['id'], block_list=block_list, block_dict=block_dict, maze=maze, global_grid_count=global_grid_count)
            if step_tmp == -1:
                return -1
            step += step_tmp
    return step

def check_grid_count(state, global_grid_count):
    grid = '%d,%d' % (state.x, state.y)
    if grid not in global_grid_count:
        global_grid_count[grid] = 0
    if global_grid_count[grid] >= 3:
        return False, '一个格子不能走三次'
    global_grid_count[grid] = global_grid_count[grid] + 1
    return True, global_grid_count[grid]

# 验证 路径  返回 步数
def validate_maze_path(path, block_list, maze):

    for block in block_list:
        if len(block) < 2:
            raise ValueError('模块必须包含2步以上操作!')

    block_dict = {}
    _dfs_path(path=path, block_list=block_list, block_dict=block_dict)
    state = start_state()
    n = len(maze)
    m = len(maze[0])

    end_x = n - 1
    end_y = m - 1

    global_grid_count = {}

    step = 0
    for opt in path:
        if isinstance(opt, int):
            flag = state.transform(opt=opt, maze=maze)
            if not flag:
                step = -1
                break
            flag, count = check_grid_count(state=state, global_grid_count=global_grid_count)
            if not flag:
                step = -1
                break
            step += 1
        else:
            step_tmp = run_block(state=state, block_id=opt['id'], block_list=block_list, block_dict=block_dict, maze=maze, global_grid_count=global_grid_count)
            if step_tmp == -1:
                step = -1
                break
            step += step_tmp

    if step == -1 or state.x != end_x or state.y != end_y:
        return False, '你似乎迷失在迷宫里了...'
    return True, step

if __name__ == '__main__':

    maze = random_maze(10, 10, max_height=0)

    print_maze(maze, print_height=False)

    # maze = [[[1, 1, 0], [1, 1, 0], [1, 1, 0], [0, 0, 0]], [[0, 0, 0], [0, 1, 0], [1, 0, 0], [0, 1, 0]], [[1, 1, 0], [0, 0, 0], [1, 1, 0], [0, 1, 0]], [[1, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]]
    import time

    start_time = time.time()

    flag, path = bfs_maze(maze)

    # print(path)
    #
    block_list = []
    # block_list.append((1, 0))
    # block_list.append((-1, 0))
    # block_list.append(({'id': 1}, {'id': 0}))
    # path = [{'id': 0}, 0, {'id': 2}, {'id': 1}, 0]
    #
    # print(path)

    print(validate_maze_path(path=path, block_list=block_list, maze=maze))



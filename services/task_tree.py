import asyncio

class TaskNode:
    def __init__(self, task):
        self.id = task["id"]
        self.type = task["type"]
        self.parameters = task.get("parameters", {})
        self.depends_on = task.get("depends_on", [])
        self.children = []
        self.executed = False

    def __repr__(self):
        return f"TaskNode(id={self.id}, type={self.type})"


async def check_circular_dependency(nodes):
    """检查循环依赖"""
    visited = set()
    path = set()
    
    async def dfs(node_id):
        if node_id in path:
            raise ValueError(f"Circular dependency detected involving task {node_id}")
        if node_id in visited:
            return
            
        visited.add(node_id)
        path.add(node_id)
        
        node = nodes[node_id]
        for dep_id in node.depends_on:
            await dfs(dep_id)
            
        path.remove(node_id)

    for node_id in nodes:
        await dfs(node_id)


async def build_task_tree(tasks):
    """
    构建任务执行树。
    :param tasks: JSON 中的任务列表
    :return: 根节点列表
    """
    nodes = {task["id"]: TaskNode(task) for task in tasks}
    
    # 检查循环依赖
    await check_circular_dependency(nodes)

    # 建立父子依赖关系
    for node in nodes.values():
        for dep_id in node.depends_on:
            parent = nodes.get(dep_id)
            if not parent:
                raise ValueError(f"Dependency task {dep_id} not found for task {node.id}.")
            parent.children.append(node)

    # 找到根节点（没有依赖的任务）
    root_nodes = [node for node in nodes.values() if not node.depends_on]
    return root_nodes


async def execute_task_tree(root_nodes, handle_task):
    """
    执行任务树中的任务。
    :param root_nodes: 根节点列表
    :param handle_task: 任务执行函数
    :return: 执行结果列表
    """
    results = []

    async def execute_node(node):
        if node.executed:
            return

        # 先执行当前任务
        try:
            result = await handle_task(node)
            results.append({"id": node.id, "type": node.type, "success": True, "description": result})
        except Exception as e:
            results.append({"id": node.id, "type": node.type, "success": False, "description": str(e)})

        node.executed = True

        # 再执行所有子节点
        for child in node.children:
            await execute_node(child)

    for root in root_nodes:
        await execute_node(root)

    return results

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
    """Check for circular dependencies"""
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
    Build the task execution tree.
    :param tasks: List of tasks from JSON
    :return: List of root nodes
    """
    nodes = {task["id"]: TaskNode(task) for task in tasks}
    
    # Check for circular dependencies
    await check_circular_dependency(nodes)

    # Establish parent-child relationships
    for node in nodes.values():
        for dep_id in node.depends_on:
            parent = nodes.get(dep_id)
            if not parent:
                raise ValueError(f"Dependency task {dep_id} not found for task {node.id}.")
            parent.children.append(node)

    # Find root nodes (tasks with no dependencies)
    root_nodes = [node for node in nodes.values() if not node.depends_on]
    return root_nodes


async def execute_task_tree(root_nodes, handle_task):
    """
    Execute tasks in the task tree.
    :param root_nodes: List of root nodes
    :param handle_task: Task execution function
    :return: List of execution results
    """
    results = []

    async def execute_node(node):
        if node.executed:
            return

        # Execute the current task first
        try:
            result = await handle_task(node)
            results.append({"id": node.id, "type": node.type, "success": True, "description": result})
        except Exception as e:
            results.append({"id": node.id, "type": node.type, "success": False, "description": str(e)})

        node.executed = True

        # Then execute all child nodes
        for child in node.children:
            await execute_node(child)

    for root in root_nodes:
        await execute_node(root)

    return results

```text
{
  "session_id": "session_56789",  // 会话 ID，用于标识任务链的唯一请求
  "request": {
    "tasks": [
      {
        "id": 1,  // 唯一任务标识符
        "type": "write",  // 任务类型：写入文件
        "parameters": {
          "path": "/path/to/file1.txt",  // 文件路径
          "content": "This is the content of file1."  // 写入的内容
        },
        "execution_order": 1  // 执行顺序：第一个执行
      },
      {
        "id": 2,
        "type": "read",  // 任务类型：读取文件
        "parameters": {
          "path": "/path/to/file1.txt"  // 文件路径，与写入路径一致
        },
        "depends_on": [1],  // 当前任务依赖于任务 1 的完成
        "execution_order": 2  // 执行顺序：第二个执行
      },
      {
        "id": 3,
        "type": "exec",  // 任务类型：执行命令
        "parameters": {
          "command": "cat /path/to/file1.txt"  // 执行命令，打印文件内容
        },
        "depends_on": [2],  // 当前任务依赖于任务 2 的完成
        "execution_order": 3  // 执行顺序：第三个执行
      }
    ]
  }
}
```

### **模板字段说明**

#### **顶层字段**
- **`session_id`**  
  - 唯一标识任务链的会话，用于请求和响应匹配。

- **`request`**  
  - 包含所有任务描述的节点。

#### **任务字段**
每个任务的字段说明如下：

1. **`id`**  
   - 唯一任务标识符，用于依赖引用和结果关联。

2. **`type`**  
   - 定义任务类型，例如：
     - `"write"`：写入文件。
     - `"read"`：读取文件。
     - `"exec"`：执行命令。

3. **`parameters`**  
   - 描述任务所需的参数：
     - **`path`**：目标文件路径。
     - **`content`**：写入文件的内容（仅 `write`）。
     - **`command`**：要执行的系统命令（仅 `exec`）。

4. **`execution_order`**  
   - 明确任务的全局执行顺序，数值越小优先级越高。

5. **`depends_on`**  
   - 任务依赖的前置任务列表。

### **文档字段说明**

#### **顶层字段**
- **`session_id`**  
  - 与请求一致，用于匹配任务链。

- **`response`**  
  - 包含所有任务的执行结果。

#### **任务结果字段**
每个任务的结果字段说明如下：

1. **`id`**  
   - 与请求中任务的 `id` 对应。

2. **`status`**  
   - 执行状态：
     - `"completed"`：已完成。
     - `"failed"`：执行失败。

3. **`parameters`**  
   - 任务执行时的输入参数。

4. **`result`**  
   - 执行的详细结果，包括：
     - **`message`**：结果摘要。
     - **`content`**：读取文件的内容（仅 `read`）。
     - **`output`**：命令输出（仅 `exec`）。

### **用途总结**

- **模板**：定义任务链及其顺序、依赖和执行参数。  
- **文档**：记录任务执行状态和结果，用于追踪和调试。
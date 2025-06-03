# Instruction Mapping Migration Guide

## 问题描述

`instruction_mapping.json` 文件目前依赖本地项目中存在这个文件，但应该像 `settings.yaml` 一样能够从依赖仓库 `criticsearch` 中直接读取。

## 解决方案

### 1. 新的工具模块

我们创建了 `ragen/utils/instruction_loader.py` 模块，它使用 `importlib.resources` 从 `criticsearch` 包中读取资源文件：

```python
from ragen.utils.instruction_loader import load_instruction_mapping, get_instruction_for_file

# 加载完整的指令映射
mapping = load_instruction_mapping()

# 获取特定文件的指令
instruction = get_instruction_for_file("2024_Botswana_general_election.json")
```

### 2. 实现模式

新的实现遵循已有的模式，参考 `ragen/env/deep_research/env_backup.py` 第 42-47 行：

```python
# 现有的模式（来自 criticsearch 包读取 benchmark 文件）
pkg = "criticsearch.reportbench.wiki_data"
with (
    __import__("importlib.resources").resources.files(pkg).
    joinpath(cfg.benchmark_file)
) as jf:
    self.benchmark = ReportBenchmark(str(jf))

# 新的模式（读取 instruction_mapping.json）
pkg = "criticsearch.data"  # 或其他适当的包路径
with (
    __import__("importlib.resources").resources.files(pkg).
    joinpath("instruction_mapping.json")
) as instruction_file:
    with open(instruction_file, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
```

### 3. 后备机制

新的实现包含后备机制：
1. 首先尝试从 `criticsearch` 包中读取
2. 如果失败，回退到本地文件读取
3. 如果都失败，返回空字典并记录警告

### 4. 使用示例

#### 基本使用
```python
from ragen.utils.instruction_loader import load_instruction_mapping

# 加载指令映射
mapping = load_instruction_mapping()
if mapping:
    print(f"成功加载 {len(mapping)} 条指令")
```

#### 在环境中使用
```python
from ragen.env.deep_research.enhanced_env import EnhancedDeepResearchEnv

# 使用增强版环境，它会自动从 criticsearch 包中加载指令
env = EnhancedDeepResearchEnv()
obs = env.reset()

# 检查是否成功加载指令映射
if env.instruction_mapping:
    print(f"已加载 {len(env.instruction_mapping)} 条指令")
```

### 5. 迁移步骤

如果你当前有代码直接读取本地 `instruction_mapping.json` 文件：

**之前的代码：**
```python
import json

# 错误的方式：依赖本地文件
with open("instruction_mapping.json", 'r') as f:
    mapping = json.load(f)
```

**迁移后的代码：**
```python
from ragen.utils.instruction_loader import load_instruction_mapping

# 正确的方式：从 criticsearch 包中读取，带本地后备
mapping = load_instruction_mapping()
```

### 6. 配置包路径

如果 `instruction_mapping.json` 位于 `criticsearch` 包的不同位置，可以指定包名：

```python
# 尝试不同的包路径
possible_packages = [
    "criticsearch.data",
    "criticsearch.resources", 
    "criticsearch.reportbench.data",
    "criticsearch"
]

for pkg in possible_packages:
    mapping = load_instruction_mapping(pkg)
    if mapping:
        print(f"从 {pkg} 成功加载")
        break
```

### 7. 与现有代码集成

新的工具与现有的 CriticSearch 集成模式保持一致：

```python
class YourEnvironment:
    def __init__(self):
        # 加载 CriticSearch 组件
        self.agent = BaseAgent()
        
        # 加载指令映射（新增）
        self.instruction_mapping = load_instruction_mapping()
        
        # 现有的 benchmark 加载（参考）
        pkg = "criticsearch.reportbench.wiki_data"
        with (__import__("importlib.resources").resources.files(pkg).
              joinpath("some_file.json")) as f:
            self.benchmark = SomeBenchmark(str(f))
```

### 8. 优势

- **一致性**：与现有的从 `criticsearch` 包读取资源的模式一致
- **可靠性**：包含后备机制，确保向后兼容
- **可维护性**：集中管理资源文件读取逻辑
- **部署简化**：不再需要在部署时确保本地文件存在

### 9. 测试

运行示例来测试新的实现：

```bash
# 运行示例脚本
python examples/load_instruction_example.py

# 测试增强版环境
python ragen/env/deep_research/enhanced_env.py
```

### 10. 注意事项

1. 确保 `criticsearch` 包中确实包含 `instruction_mapping.json` 文件
2. 如果文件位置不同，需要调整包路径
3. 新的实现保持向后兼容，现有代码可以逐步迁移 
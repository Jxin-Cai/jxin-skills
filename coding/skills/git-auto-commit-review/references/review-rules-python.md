# 代码审查规则 — Python

Python 项目特定的审查规则。仅在项目使用 Python 技术栈时加载。

通用规则见 `review-rules.md`。

## 目录

- [类型与安全](#类型与安全)
- [异常处理](#异常处理)
- [性能](#性能)
- [资源管理](#资源管理)
- [并发](#并发)
- [代码风格与惯例](#代码风格与惯例)
- [依赖与打包](#依赖与打包)
- [Web 框架（Django/Flask/FastAPI）](#web-框架djangoflaskfastapi)

---

## 类型与安全

1. **生产代码推荐使用类型注解（P2）**
   - **原因**：类型注解提升可读性、便于 IDE 分析和 mypy 检查
   - **反例**：`def process(data, config): ...` 无任何类型标注
   - **正例**：`def process(data: list[dict], config: AppConfig) -> Result: ...`

2. **避免使用 eval/exec 处理外部输入（P0）**
   - **原因**：直接执行任意代码，是最严重的注入漏洞
   - **反例**：`eval(user_input)` 或 `exec(request.body)`
   - **正例**：使用 `ast.literal_eval` 解析字面量；或用 JSON 解析

3. **subprocess 使用列表参数而非字符串（P0）**
   - **原因**：字符串参数 + shell=True 存在命令注入风险
   - **反例**：`subprocess.run(f"convert {filename} output.png", shell=True)`
   - **正例**：`subprocess.run(["convert", filename, "output.png"])`

4. **SQL 查询使用参数化而非字符串拼接（P0）**
   - **原因**：字符串拼接是 SQL 注入的根源
   - **反例**：`cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")`
   - **正例**：`cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))`

## 异常处理

1. **禁止裸 except（P0）**
   - **原因**：`except:` 捕获所有异常（含 KeyboardInterrupt、SystemExit），隐藏严重错误
   - **反例**：`except:` 或 `except Exception:` 然后 `pass`
   - **正例**：捕获具体异常类型：`except ValueError as e: ...`；必须用宽泛捕获时至少记录日志

2. **异常信息要包含上下文（P1）**
   - **原因**：无上下文的异常在生产环境中极难排查
   - **反例**：`raise ValueError("invalid input")`
   - **正例**：`raise ValueError(f"invalid user_id={user_id!r}: must be positive integer")`

3. **使用 raise ... from 保留异常链（P2）**
   - **原因**：丢失原始异常会增加调试难度
   - **反例**：`except KeyError: raise ValueError("missing field")`
   - **正例**：`except KeyError as e: raise ValueError("missing field") from e`

## 性能

1. **避免在循环中重复查询或 I/O（P0）**
   - **原因**：N+1 问题在 Python 中同样常见
   - **反例**：`for user in users: profile = db.query(Profile).filter_by(user_id=user.id).first()`
   - **正例**：批量查询：`profiles = db.query(Profile).filter(Profile.user_id.in_(user_ids)).all()`

2. **大数据处理使用生成器（P1）**
   - **原因**：一次性加载大数据集到内存会导致 OOM
   - **反例**：`data = file.readlines()` 读取 GB 级文件
   - **正例**：`for line in file:` 逐行处理；或使用生成器表达式

3. **字符串拼接避免在循环中用 +（P2）**
   - **原因**：字符串不可变，循环中 + 拼接产生 O(n²) 开销
   - **反例**：`result = ""; for s in items: result += s`
   - **正例**：`result = "".join(items)`

## 资源管理

1. **文件和连接使用 with 语句（P0）**
   - **原因**：不使用上下文管理器可能导致资源泄露
   - **反例**：`f = open("data.txt"); data = f.read()` 未关闭文件
   - **正例**：`with open("data.txt") as f: data = f.read()`

2. **数据库连接/会话要及时释放（P1）**
   - **原因**：连接泄露会耗尽连接池
   - **反例**：创建 session 但未在 finally 中关闭
   - **正例**：使用上下文管理器或 try-finally 确保释放

## 并发

1. **多线程共享状态要加锁（P0）**
   - **原因**：Python 的 GIL 不保证复合操作的原子性
   - **反例**：多线程共享 dict/list 并发读写不加锁
   - **正例**：使用 `threading.Lock`、`Queue` 或线程安全的数据结构

2. **asyncio 代码禁止在事件循环中调用阻塞操作（P0）**
   - **原因**：阻塞调用会卡住整个事件循环
   - **反例**：在 async 函数中直接调用 `requests.get()` 或 `time.sleep()`
   - **正例**：使用 `aiohttp` 等异步库；或用 `asyncio.to_thread()` 包装阻塞调用

## 代码风格与惯例

1. **遵循 PEP 8 命名约定（P2）**
   - **原因**：一致的命名降低认知负担
   - **反例**：混用 `camelCase` 和 `snake_case`；类名用小写
   - **正例**：函数/变量用 `snake_case`；类名用 `PascalCase`；常量用 `UPPER_SNAKE_CASE`

2. **使用 pathlib 替代 os.path（P2）**
   - **原因**：pathlib 更安全、可读性更好、跨平台兼容性更强
   - **反例**：`os.path.join(base_dir, "data", filename)`
   - **正例**：`Path(base_dir) / "data" / filename`

3. **可变默认参数要用 None（P0）**
   - **原因**：可变默认参数在函数定义时创建一次，后续调用共享同一对象
   - **反例**：`def add_item(item, items=[]): items.append(item); return items`
   - **正例**：`def add_item(item, items=None): items = items if items is not None else []; ...`

## 依赖与打包

1. **锁定依赖版本（P1）**
   - **原因**：未锁定的依赖导致不可重现的构建
   - **反例**：`requirements.txt` 只写 `requests` 不带版本号
   - **正例**：使用 `poetry.lock`、`pip-tools` 的 requirements.txt 或 `uv.lock`

2. **区分运行时依赖和开发依赖（P2）**
   - **原因**：部署时不需要 pytest、mypy 等开发工具
   - **反例**：所有依赖放在同一个 `requirements.txt` 中
   - **正例**：使用 `pyproject.toml` 的 `[project.optional-dependencies]` 或独立的 `requirements-dev.txt`

## Web 框架（Django/Flask/FastAPI）

1. **请求输入要做校验和清洗（P0）**
   - **原因**：信任用户输入是安全漏洞的根源
   - **反例**：直接使用 `request.json["email"]` 不做校验
   - **正例**：Django 用 Form/Serializer；FastAPI 用 Pydantic model；Flask 用 marshmallow

2. **数据库迁移要可逆（P1）**
   - **原因**：不可逆的迁移在回滚时会造成数据丢失
   - **反例**：`DROP COLUMN` 不做数据备份
   - **正例**：迁移脚本包含 forward 和 backward 操作；破坏性迁移先备份数据

3. **避免在视图/路由中直接写业务逻辑（P1）**
   - **原因**：视图层代码难以复用和测试
   - **反例**：所有业务逻辑写在 view 函数中，200+ 行
   - **正例**：视图层只做请求解析和响应封装；业务逻辑抽到 service 层

# 代码审查规则 — Go

Go 项目特定的审查规则。仅在项目使用 Go 技术栈时加载。

通用规则见 `review-rules.md`。

## 目录

- [错误处理](#错误处理)
- [并发与 Goroutine](#并发与-goroutine)
- [资源管理](#资源管理)
- [接口与类型设计](#接口与类型设计)
- [性能](#性能)
- [安全](#安全)
- [代码风格与惯例](#代码风格与惯例)
- [依赖与模块](#依赖与模块)

---

## 错误处理

1. **error 必须处理，禁止忽略（P0）**
   - **原因**：Go 的错误处理依赖显式检查，忽略 error 是静默失败的根源
   - **反例**：`result, _ := doSomething()` 直接丢弃 error
   - **正例**：`result, err := doSomething(); if err != nil { return fmt.Errorf("doSomething failed: %w", err) }`

2. **错误要包装上下文再向上传播（P1）**
   - **原因**：无上下文的 error 在调用链中极难定位来源
   - **反例**：`return err`（原样传播，丢失调用层信息）
   - **正例**：`return fmt.Errorf("processing user %d: %w", userID, err)`

3. **不要用 panic 处理可恢复的错误（P0）**
   - **原因**：panic 会中断正常控制流，在服务端可能导致整个请求处理崩溃
   - **反例**：`if input == "" { panic("empty input") }`
   - **正例**：`if input == "" { return nil, errors.New("input must not be empty") }`

4. **sentinel error 使用 errors.Is/errors.As 比较（P1）**
   - **原因**：直接 `==` 比较在 error 被包装后会失效
   - **反例**：`if err == sql.ErrNoRows { ... }`
   - **正例**：`if errors.Is(err, sql.ErrNoRows) { ... }`

## 并发与 Goroutine

1. **goroutine 必须有退出机制（P0）**
   - **原因**：泄露的 goroutine 持续消耗内存和 CPU，且无法被 GC 回收
   - **反例**：`go func() { for { processItem(<-ch) } }()` 无退出条件
   - **正例**：使用 `context.Context` 或 `done` channel 控制生命周期

2. **并发访问共享数据要加锁或使用 channel（P0）**
   - **原因**：Go 的 map 和 slice 不是并发安全的
   - **反例**：多个 goroutine 直接读写同一个 map
   - **正例**：使用 `sync.Mutex`、`sync.RWMutex`、`sync.Map` 或 channel 传递数据

3. **启动 goroutine 要处理 panic（P0）**
   - **原因**：goroutine 中未 recover 的 panic 会导致整个进程崩溃
   - **反例**：`go handleRequest(req)` 且 handleRequest 可能 panic
   - **正例**：在 goroutine 入口处 `defer func() { if r := recover(); r != nil { log.Error(...) } }()`

4. **使用 errgroup 管理并发任务（P2）**
   - **原因**：手动管理 WaitGroup + error 收集容易出错
   - **反例**：手写 WaitGroup + 手动收集第一个错误
   - **正例**：`g, ctx := errgroup.WithContext(ctx); g.Go(func() error { ... }); if err := g.Wait(); ...`

5. **channel 要有明确的关闭责任方（P1）**
   - **原因**：向已关闭的 channel 发送会 panic；未关闭的 channel 可能导致 goroutine 泄露
   - **反例**：多个 goroutine 都可能关闭同一个 channel
   - **正例**：只有发送方关闭 channel；用 sync.Once 保证只关闭一次

## 资源管理

1. **HTTP Response Body 必须关闭（P0）**
   - **原因**：不关闭会泄露连接，最终耗尽连接池
   - **反例**：`resp, _ := http.Get(url)` 未调用 `resp.Body.Close()`
   - **正例**：`resp, err := http.Get(url); if err != nil { return err }; defer resp.Body.Close()`

2. **数据库行/语句要及时关闭（P0）**
   - **原因**：未关闭的 rows/stmt 泄露数据库连接
   - **反例**：`rows, _ := db.Query(...)` 未 `defer rows.Close()`
   - **正例**：`rows, err := db.Query(...); if err != nil { return err }; defer rows.Close()`

3. **defer 在错误检查之后（P1）**
   - **原因**：在 nil 资源上 defer Close 会 panic
   - **反例**：`resp, err := http.Get(url); defer resp.Body.Close(); if err != nil { ... }`
   - **正例**：`resp, err := http.Get(url); if err != nil { return err }; defer resp.Body.Close()`

## 接口与类型设计

1. **接口要小（P1）**
   - **原因**：Go 谚语"The bigger the interface, the weaker the abstraction"
   - **反例**：定义一个 10 个方法的接口，大部分实现只用其中 2 个
   - **正例**：1-3 个方法的小接口；需要时通过接口组合扩展

2. **在消费方定义接口，不在实现方（P1）**
   - **原因**：Go 的隐式接口实现让消费方定义接口成为最佳实践
   - **反例**：在 package A 中定义接口，要求 package B 实现
   - **正例**：在需要抽象的 package 中定义最小接口

3. **导出的结构体字段要有 json tag（P2）**
   - **原因**：Go 默认使用字段名作为 JSON key，大小写不符合 API 惯例
   - **反例**：`type User struct { UserName string }` → 序列化为 `{"UserName":...}`
   - **正例**：`type User struct { UserName string \`json:"user_name"\` }`

## 性能

1. **预分配 slice 容量（P2）**
   - **原因**：避免 append 过程中的多次扩容和内存拷贝
   - **反例**：`var result []int; for ... { result = append(result, v) }`
   - **正例**：`result := make([]int, 0, len(source))`

2. **避免在热路径中频繁创建短生命周期对象（P2）**
   - **原因**：增加 GC 压力
   - **反例**：每次请求都 new 一个 buffer
   - **正例**：使用 `sync.Pool` 复用对象

3. **字符串拼接使用 strings.Builder（P2）**
   - **原因**：`+` 拼接在循环中产生大量临时字符串
   - **反例**：`result := ""; for _, s := range items { result += s }`
   - **正例**：`var b strings.Builder; for _, s := range items { b.WriteString(s) }`

## 安全

1. **SQL 查询使用参数化（P0）**
   - **原因**：字符串拼接是 SQL 注入的根源
   - **反例**：`db.Query("SELECT * FROM users WHERE id = " + userID)`
   - **正例**：`db.Query("SELECT * FROM users WHERE id = $1", userID)`

2. **HTTP 客户端要设置超时（P0）**
   - **原因**：默认的 `http.DefaultClient` 无超时，可能永久阻塞
   - **反例**：`http.Get(url)` 使用默认客户端
   - **正例**：`client := &http.Client{Timeout: 10 * time.Second}`

3. **模板渲染使用 html/template 而非 text/template（P0）**
   - **原因**：`text/template` 不做 HTML 转义，存在 XSS 风险
   - **反例**：用 `text/template` 渲染包含用户输入的 HTML
   - **正例**：Web 页面渲染使用 `html/template`

## 代码风格与惯例

1. **命名遵循 Go 惯例（P2）**
   - **原因**：Go 社区有强烈的命名共识，违反会降低可读性
   - **反例**：`getUserByID` → Go 惯例应为 `GetUserByID`（导出）或 `userByID`（未导出）
   - **正例**：缩写全大写（`ID`、`HTTP`、`URL`）；getter 不加 `Get` 前缀（`user.Name()` 而非 `user.GetName()`）

2. **包名简短且小写（P2）**
   - **原因**：包名是调用方的前缀，太长会影响可读性
   - **反例**：`package userManagementService`
   - **正例**：`package user`

3. **避免 init() 函数的副作用（P1）**
   - **原因**：init() 的执行顺序隐式且难以测试
   - **反例**：在 init() 中连接数据库或启动后台任务
   - **正例**：在 main() 或显式初始化函数中执行副作用操作

## 依赖与模块

1. **go.sum 要提交到版本控制（P1）**
   - **原因**：go.sum 保证依赖完整性和可重现构建
   - **反例**：.gitignore 排除了 go.sum
   - **正例**：go.mod 和 go.sum 都提交

2. **避免引入过重的依赖（P2）**
   - **原因**：Go 的二进制会包含所有依赖的代码
   - **反例**：为了一个 JSON 工具函数引入整个大框架
   - **正例**：评估依赖大小和必要性；简单功能优先用标准库

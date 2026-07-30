# 风格指纹系统

> 设计参考：`GeekyWizKid/writing-helper` 的多维风格编辑器、固定表达和可复用风格提示词。

## Profile Schema

```yaml
name: 风格名称
tone: professional-casual
humor_level: 6
analogy_density: high
sentence_max_length: 45
paragraph_max_sentences: 6
signature_phrases: []
forbidden_phrases: []
code_comment_style: chinese
transition_style: natural
opening_preference: [question, humor, case, direct]
```

字段规则：

- `tone`：`professional`、`professional-casual` 或 `balanced`。
- `humor_level`：0-10，只控制幽默频率，不要求每节插梗。
- `analogy_density`：`low`、`medium`、`high`。
- `sentence_max_length`：软上限；代码、URL 和必要长句例外。
- `paragraph_max_sentences`：段落节奏参考，不机械截断。
- `signature_phrases`：少量标志性表达，每篇选择性使用，避免口头禅堆叠。
- `forbidden_phrases`：默认不使用；技术引用需要时可豁免。
- `opening_preference`：按优先级选择开场方式。

## 使用方式

1. 未指定时加载 `default-sanqi.yaml`。
2. 用户说“切换风格 formal-tech”时，加载对应 YAML。
3. 写大纲前把 profile 转成写作约束；完稿后再做一次风格合规检查。
4. 风格约束与技术准确性冲突时，以准确性为先。
5. 不混合多个 profile；用户确有需求时先合成一个临时 profile。

## 自动提取

从 3 篇以上同一作者文章提取效果更稳定：

```bash
python scripts/extract_style.py \
  --articles-dir ./articles \
  --output references/style-profiles/custom.yaml
```

脚本统计句长、段落长度、类比密度、幽默标记、语气和重复特色短语。自动结果是草稿，应人工删除偶然高频词和不希望固化的表达。

## 合规检查

完稿后检查：

- 语气与 `tone` 一致。
- 句长和段落节奏大部分落在 profile 范围内。
- 类比帮助理解，没有喧宾夺主。
- 标志性表达自然且克制。
- 禁用短语未出现，或有明确技术语境。
- 幽默不削弱严肃结论，不虚构个人经历。

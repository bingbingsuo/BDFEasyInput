# BDFEasyInput 功能总结

**最后更新**: 2025年12月12日

## 🎯 核心功能

### 1. 输入转换
- ✅ YAML/JSON → BDF 输入文件
- ✅ 支持所有主要计算类型
- ✅ 智能关键词映射
- ✅ 输入验证和错误检查

### 2. 计算执行
- ✅ 直接执行模式（BDFDirectRunner）
- ✅ BDFAutotest 集成模式
- ✅ 自动环境配置
- ✅ Debug 目录支持

### 3. 结果分析
- ✅ 输出文件解析
- ✅ AI 专家级分析
- ✅ 多格式报告生成
- ✅ 中英文双语支持

### 4. AI 辅助
- ✅ 自然语言任务规划
- ✅ 多服务商支持（9 个）
- ✅ 本地模型支持（Ollama）

## 🌟 最新功能亮点

### 激发态溶剂效应支持 ⭐

#### cLR（线性响应非平衡溶剂化）
- 在 TDDFT 块中自动添加 `solneqlr` 关键词
- 支持线性响应理论计算非平衡溶剂效应

#### ptSS（态特定微扰理论）
- 自动生成 2 个 TDDFT 块 + 1 个 RESP 块
- 基于 resp 的一阶微扰校正
- 提取校正后的垂直激发能
- 显示非平衡/平衡溶剂化自由能

### 增强的解析功能 ⭐

- ✅ TDA vs TDDFT 正确识别
- ✅ JK 算符内存信息提取
- ✅ 效率提示（MEMJKOP 建议）
- ✅ 非平衡溶剂化校正提取
- ✅ 方法自动识别（cLR vs ptSS）

## 📝 使用示例

### 完整工作流示例

```bash
# 1. 从 YAML 生成 BDF 输入
bdfeasyinput convert example.yaml -o input.inp

# 2. 运行计算
bdfeasyinput run input.inp

# 3. 分析结果
bdfeasyinput analyze output.log --input input.inp
```

### 激发态溶剂效应示例

参见 `docs/dev/CURRENT_STATUS_2025.md` 中的 YAML 配置示例。

## 🔧 技术架构

- **语言**: Python 3.7+
- **核心库**: PyYAML, Click
- **AI 集成**: OpenAI 兼容接口
- **模块化设计**: 易于扩展和维护

## 📚 文档

- 开发文档: `docs/dev/`
- 用户指南: `docs/`
- 示例文件: `examples/`
- 测试文件: `tests/`

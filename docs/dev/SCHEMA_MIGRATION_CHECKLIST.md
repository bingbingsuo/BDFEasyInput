# Schema 迁移检查清单

## ✅ 已完成项目

### 代码迁移
- [x] 重写 `bdfeasyinput/validator.py` 使用 schema
- [x] 移除重复的枚举定义（TaskType, MethodType, CoordinateUnit）
- [x] 更新 `bdfeasyinput/__init__.py` 导出 schema 类型
- [x] 保持公共接口向后兼容
- [x] 改进错误处理和错误信息

### 文档更新
- [x] 创建迁移完成报告 (`SCHEMA_MIGRATION_COMPLETE.md`)
- [x] 创建迁移总结 (`MIGRATION_SUMMARY.md`)
- [x] 更新 README.md 安装说明
- [x] 更新 Schema 分析文档

### 依赖配置
- [x] `requirements.txt` 中已包含 `bdfeasyinput-schema`
- [x] 依赖路径正确配置

## 🔄 待完成项目

### 测试验证
- [ ] 运行完整测试套件
  ```bash
  pytest tests/
  ```
- [ ] 验证 validator 功能
  ```bash
  pytest tests/test_validator.py -v
  ```
- [ ] 验证 converter 功能
  ```bash
  pytest tests/test_converter.py -v
  ```
- [ ] 验证 CLI 功能
  ```bash
  python -m bdfeasyinput.cli validate-yaml examples/h2o_pbe0.yaml
  ```

### 集成测试
- [ ] 测试与 BDFAgent 的兼容性
  - 使用 BDFAgent 生成的 YAML 文件
  - 验证 BDFEasyInput 可以正确处理
- [ ] 测试错误处理
  - 无效的 YAML 配置
  - 缺失必需字段
  - 类型错误

### 文档完善
- [ ] 更新用户手册中的验证部分
- [ ] 添加 schema 使用示例
- [ ] 更新 API 文档

### 发布准备
- [ ] 更新版本号（如果需要）
- [ ] 更新 CHANGELOG.md
- [ ] 检查所有导入语句
- [ ] 验证安装流程

## 📋 验证步骤

### 1. 基本功能验证

```bash
# 1. 确保 schema 包已安装
python -c "import bdfeasyinput_schema; print('✓ Schema installed')"

# 2. 测试导入
python -c "from bdfeasyinput import BDFValidator; print('✓ Validator imported')"

# 3. 测试基本验证
python -c "
from bdfeasyinput import BDFValidator
import yaml

config = {
    'task': {'type': 'energy'},
    'molecule': {'name': 'test', 'charge': 0, 'multiplicity': 1, 'coordinates': ['H 0 0 0']},
    'method': {'type': 'dft', 'functional': 'pbe0', 'basis': 'cc-pvdz'}
}

validator = BDFValidator()
result, warnings = validator.validate(config)
print('✓ Validation successful')
"
```

### 2. 错误处理验证

```bash
# 测试无效配置
python -c "
from bdfeasyinput import BDFValidator, ValidationError

validator = BDFValidator()
try:
    validator.validate({'invalid': 'config'})
except ValidationError as e:
    print('✓ Error handling works:', str(e)[:50])
"
```

### 3. 文件验证

```bash
# 使用示例文件测试
python -m bdfeasyinput.cli validate-yaml examples/h2o_pbe0.yaml
```

## 🎯 成功标准

迁移成功的标准：

1. ✅ 所有现有测试通过
2. ✅ 可以正常导入和使用 validator
3. ✅ 错误处理正常工作
4. ✅ 与 BDFAgent 生成的 YAML 兼容
5. ✅ 文档已更新

## 📝 注意事项

1. **依赖安装顺序**：
   - 必须先安装 `bdfeasyinput_schema`
   - 然后安装 `bdfeasyinput`

2. **向后兼容性**：
   - 公共接口保持不变
   - 现有代码无需修改
   - `use_pydantic` 参数已废弃但保留

3. **错误信息**：
   - 现在使用 Pydantic 的详细错误信息
   - 错误定位更准确

## 🔗 相关文档

- [迁移完成报告](./SCHEMA_MIGRATION_COMPLETE.md)
- [Schema 必须依赖分析](./SCHEMA_REQUIRED_DEPENDENCY_ANALYSIS.md)
- [Schema 模块分析](./BDFEASYINPUT_SCHEMA_ANALYSIS.md)
- [迁移总结](../../MIGRATION_SUMMARY.md)

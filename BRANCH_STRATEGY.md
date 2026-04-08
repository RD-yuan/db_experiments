# Git 分支策略

## 分支结构

```
main (生产环境)
  ↑
  └── dev (开发集成分支)
        ├── backend (后端开发)
        └── frontend (前端开发)
```

## 分支说明

| 分支 | 用途 | 说明 |
|------|------|------|
| **main** | 生产环境 | 稳定版本，只有经过测试的代码才能合并 |
| **dev** | 开发集成分支 | backend 和 frontend 合并到这里进行集成测试 |
| **backend** | 后端开发 | Flask 后端代码开发 |
| **frontend** | 前端开发 | Vue3 前端代码开发 |

---

## 工作流程

### 1. 后端开发
```bash
# 切换到 backend 分支
git checkout backend

# 开发后端功能...
# 修改 backend/ 目录下的代码

# 提交代码
git add .
git commit -m "feat: 添加XXX功能"
git push

# 合并到 dev 分支
git checkout dev
git merge backend
git push

# 解决冲突（如果有）
# 然后推送
```

### 2. 前端开发
```bash
# 切换到 frontend 分支
git checkout frontend

# 开发前端功能...
# 修改 frontend/ 目录下的代码

# 提交代码
git add .
git commit -m "feat: 添加XXX页面"
git push

# 合并到 dev 分支
git checkout dev
git merge frontend
git push
```

### 3. 发布到生产环境
```bash
# dev 分支测试通过后，合并到 main
git checkout main
git merge dev
git push

# 打标签
git tag -a v1.0.0 -m "版本 1.0.0"
git push origin v1.0.0
```

---

## 快捷命令

### 查看所有分支
```bash
git branch -a
```

### 查看当前分支
```bash
git branch
```

### 切换分支
```bash
git checkout <branch-name>
```

### 合并分支
```bash
git checkout dev
git merge backend
```

### 删除本地分支
```bash
git branch -d <branch-name>
```

### 删除远程分支
```bash
git push origin --delete <branch-name>
```

---

## 注意事项

1. **不要直接在 main 分支开发**
2. **backend 和 frontend 分支只修改对应的代码**
3. **合并前先 pull 最新代码**
4. **冲突时及时解决**
5. **提交信息要清晰明确**

---

## 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复bug |
| docs | 文档更新 |
| style | 代码格式调整 |
| refactor | 重构代码 |
| test | 测试相关 |
| chore | 构建/工具相关 |

示例：
```bash
git commit -m "feat: 添加用户登录功能"
git commit -m "fix: 修复订单库存扣减bug"
git commit -m "docs: 更新API文档"
```

---

## 当前分支状态

- ✅ main - 生产环境（初始版本）
- ✅ dev - 开发集成分支
- ✅ backend - 后端开发分支
- ✅ frontend - 前端开发分支

所有分支已同步到 GitHub。

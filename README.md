# Jounal RSS Rater

- 从多个RSS源获取最新文章数据
- 使用和OpenAI兼容的LLM模型对文章相关性进行评分

## 部署

克隆仓库：
```bash
git clone git@github.com:RibomBalt/journal-rss-rater.git
```

使用包管理器[uv](https://docs.astral.sh/uv/getting-started/installation/)安装后端依赖。
```bash
uv sync
``` 

前端使用`node.js`编译（在`v18`经过测试），包管理器使用`yarn`。请在[官方下载页面](https://nodejs.org/zh-cn/download)下载并安装`node.js+yarn`。用以下命令安装前端依赖并构建：
```bash
# 进入前端目录。注意，请不要在根目录执行yarn等命令，也不要混用包管理器（npm等）
cd frontend
# 安装依赖
yarn
# 构建（指定前缀）
yarn build --base="/rss"
```
构建后的前端代码将位于`frontend/dist`目录下。前端代码修改后必须要重新构建才可生效。

如要运行后端，请在根目录执行命令：
```bash
uv run python -m backend.main
```

如果进行单元测试，可以进行：
```bash
uv run pytest -s backend/tests/{your-test-file}.py
```

## 配置

后端配置文件包括：
#### `backend/config/default.yml`：默认后端配置

- 建议部署时复制`default.yml`到同目录`dev.yml`，并将任意私密配置（如LLM API KEY）放在`dev.yml`中，并不要修改`default.yml`。当存在`dev.yml`时，后端会自动读取并忽略`default.yml`。
- `ADMIN_PANEL`下的`token`是访问管理员面板时HTTP Digest验证的令牌，请按注释方法生成并写入`dev.yml`

#### `backend/config/logging.yml`：日志配置
#### `backend/config/rss.yml`：RSS源配置

- 建议修改后，通过`backend/tests/test_models.py`进行测试

## 测试
目前的后端测试位于`backend/tests`：

- `test_feedparser.py`：测试`feedparser`库
- `test_models.py`：测试`rss.yml`配置下RSS源能否正常获取文章
- `test_rater.py`：测试LLM对文章的评分功能

## 技术栈
- 后端：Python, FastAPI
- 前端：Vue.js, TypeScript
- 数据库：SQLite，SQLAlchemy
- 数据验证：Pydantic
- 计时任务：APScheduler
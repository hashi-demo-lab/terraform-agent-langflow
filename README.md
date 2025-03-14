# terraform-agent-langflow

```zsh
uv venv --python 3.11 langflow
source langflow/bin/activate
```

```zsh
uv pip install langflow
```

When running the command below there might be errors printed out. You may ignore these errors, LangFlow still works despite these.

```zsh
uv run langflow run --log-level debug
```
## Install Ollama

```zsh
brew install ollama
brew services start ollama
```

### Run qwen2.5 14b (smaller model for M1 mac)
```zsh
ollama run qwen2.5-coder:14b
```


### Run qwq
```zsh
ollama run qwq
```

## install Watsonx-ai SDK
```zsh
source langflow/bin/activate
uv pip install ibm-watsonx-ai
uv pip install langchain-ibm
uv pip install --upgrade ibm-cloud-sdk-core
```



## Open LangFlow

http://127.0.0.1:7862/


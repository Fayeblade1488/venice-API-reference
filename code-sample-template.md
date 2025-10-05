# Code Sample Templates

This file contains the canonical code samples for the Venice.ai API. These examples should be used as a template when adding `x-codeSamples` to new endpoints in the OpenAPI specification.

## cURL

```yaml
x-codeSamples:
  - lang: cURL
    label: "cURL"
    source: |
      curl -X POST "https://api.venice.ai/v1/chat/completions"       -H "Authorization: Bearer YOUR_API_KEY"       -H "Content-Type: application/json"       -d '{
        "model": "venice-pro",
        "messages": [{"role": "user", "content": "Hello Venice"}]
      }'
```

## Python

```yaml
  - lang: Python
    label: "Python (requests)"
    source: |
      import requests

      url = "https://api.venice.ai/v1/chat/completions"
      headers = {"Authorization": "Bearer YOUR_API_KEY"}
      data = {
          "model": "venice-pro",
          "messages": [{"role": "user", "content": "Hello Venice"}]
      }

      response = requests.post(url, json=data, headers=headers)
      print(response.json())
```

## JavaScript

```yaml
  - lang: JavaScript
    label: "JavaScript (fetch)"
    source: |
      const response = await fetch("https://api.venice.ai/v1/chat/completions", {
        method: "POST",
        headers: {
          "Authorization": "Bearer YOUR_API_KEY",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          "model": "venice-pro",
          messages: [{ role: "user", content: "Hello Venice" }]
        })
      });

      const data = await response.json();
      console.log(data);
```

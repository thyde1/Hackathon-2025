from typing import Dict
from mcp.server.fastmcp import FastMCP
import os
from openai import AzureOpenAI

mcp = FastMCP("Emojifier", port=8020)

@mcp.tool()
def emojojify_text(text: str) -> Dict[str, str]:
    """Add some vaguely related emojis to the input text
    
    Args:
        text: The input text to emojify (required)
        
    Returns:
        Dictionary with success status, message, and emojified text
    """
    # Set up Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint="ENDPOINT",
        api_key="API KEY",
        api_version="2024-12-01-preview"
    )

    deployment_name = "gpt-35-turbo"

    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are an assistant that adds appropriate emojis to text."},
                {"role": "user", "content": f"Add emojis to this text: {text}"}
            ],
            max_tokens=100
        )
        emojified = response.choices[0].message.content.strip()
        return {
            "success": "true",
            "message": "Text emojified successfully.",
            "emojified_text": emojified
        }
    except Exception as e:
        return {
            "success": "false",
            "message": f"Failed to emojify text: {str(e)}",
            "emojified_text": ""
        }
    
if __name__ == "__main__":
    mcp.run(transport="streamable-http")


# imports
from mcp.server.fastmcp import FastMCP
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# global vars
mcp = FastMCP(name="Bioindex MCP Server")


# methods
@mcp.tool()
def greeting(hint: str) -> str:
    '''
    This tool displays a greeting message

    Args:
        hint: The hint for the type of greeting
    '''
    # log
    logger.info(f"=============== Received query for greeting")

    # return
    return "Hello, myname is the Flannick Lab's remote MCP server"


# main
if __name__ == "__main__":
    mcp.settings.port = 8081
    mcp.run(transport='sse')


"""
Persist Packing List MCP Server - Manage and persist travel packing lists.

To run this server:
    uv run mcp dev main.py

Provides persistent storage for travel packing lists with full CRUD operations
and status tracking.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from mcp.server.fastmcp import FastMCP

from packing_service import PackingListService
from utils import (
    format_packing_list_response,
    format_list_summary_response,
    format_packing_item_response
)

mcp = FastMCP("Persist Packing List", port=8011)
service = PackingListService()

# Packing List Management Tools
@mcp.tool()
def create_packing_list(
    name: str,
    description: Optional[str] = None,
    destination: Optional[str] = None,
    travel_start_date: Optional[str] = None,
    travel_end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new packing list
    
    Args:
        name: Name of the packing list
        description: Optional description of the trip/list
        destination: Travel destination
        travel_start_date: Start date in ISO format (YYYY-MM-DD)
        travel_end_date: End date in ISO format (YYYY-MM-DD)
        
    Returns:
        Created packing list with ID and metadata
    """
    # Parse dates if provided
    start_date = None
    end_date = None
    
    if travel_start_date:
        try:
            start_date = datetime.fromisoformat(travel_start_date)
        except ValueError:
            pass
    
    if travel_end_date:
        try:
            end_date = datetime.fromisoformat(travel_end_date)
        except ValueError:
            pass
    
    packing_list = service.create_packing_list(
        name=name,
        description=description,
        destination=destination,
        travel_start_date=start_date,
        travel_end_date=end_date
    )
    
    return format_packing_list_response(packing_list)


@mcp.tool()
def get_packing_list(list_id: int) -> Dict[str, Any]:
    """Get a packing list by ID with all items
    
    Args:
        list_id: ID of the packing list to retrieve
        
    Returns:
        Packing list with all items and completion status
    """
    packing_list = service.get_packing_list(list_id)
    
    if not packing_list:
        return {"error": f"Packing list with ID {list_id} not found"}
    
    return format_packing_list_response(packing_list)


@mcp.tool()
def list_all_packing_lists() -> Dict[str, Any]:
    """Get all packing lists with summary information
    
    Returns:
        List of all packing lists with basic info and completion status
    """
    summaries = service.list_packing_lists()
    
    return {
        "packing_lists": [format_list_summary_response(summary) for summary in summaries],
        "total_count": len(summaries)
    }


@mcp.tool()
def update_packing_list(
    list_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    destination: Optional[str] = None,
    travel_start_date: Optional[str] = None,
    travel_end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Update an existing packing list
    
    Args:
        list_id: ID of the packing list to update
        name: New name for the list (optional)
        description: New description (optional)
        destination: New destination (optional)
        travel_start_date: New start date in ISO format (optional)
        travel_end_date: New end date in ISO format (optional)
        
    Returns:
        Updated packing list
    """
    # Parse dates if provided
    start_date = None
    end_date = None
    
    if travel_start_date:
        try:
            start_date = datetime.fromisoformat(travel_start_date)
        except ValueError:
            pass
    
    if travel_end_date:
        try:
            end_date = datetime.fromisoformat(travel_end_date)
        except ValueError:
            pass
    
    packing_list = service.update_packing_list(
        list_id=list_id,
        name=name,
        description=description,
        destination=destination,
        travel_start_date=start_date,
        travel_end_date=end_date
    )
    
    if not packing_list:
        return {"error": f"Packing list with ID {list_id} not found"}
    
    return format_packing_list_response(packing_list)


@mcp.tool()
def delete_packing_list(list_id: int) -> Dict[str, Any]:
    """Delete a packing list and all its items
    
    Args:
        list_id: ID of the packing list to delete
        
    Returns:
        Success status and message
    """
    success = service.delete_packing_list(list_id)
    
    if success:
        return {
            "success": True,
            "message": f"Packing list {list_id} deleted successfully"
        }
    else:
        return {
            "success": False,
            "error": f"Packing list with ID {list_id} not found"
        }


# Packing Item Management Tools
@mcp.tool()
def add_item_to_list(
    list_id: int,
    name: str,
    category: str = "miscellaneous",
    quantity: int = 1,
    status: str = "not_packed",
    notes: Optional[str] = None,
    priority: int = 1
) -> Dict[str, Any]:
    """Add an item to a packing list
    
    Args:
        list_id: ID of the packing list
        name: Name of the item
        category: Item category (clothing, electronics, toiletries, documents, medications, entertainment, food_snacks, sports_outdoor, miscellaneous)
        quantity: Number of items needed (default: 1)
        status: Packing status (not_packed, packed, optional)
        notes: Optional notes about the item
        priority: Priority level 1-5, with 5 being highest (default: 1)
        
    Returns:
        Created packing item
    """
    item = service.add_item_to_list(
        list_id=list_id,
        name=name,
        category=category,
        quantity=quantity,
        status=status,
        notes=notes,
        priority=priority
    )
    
    if not item:
        return {"error": f"Packing list with ID {list_id} not found"}
    
    return format_packing_item_response(item)


@mcp.tool()
def update_item_status(
    item_id: int,
    status: str,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """Update an item's packing status
    
    Args:
        item_id: ID of the item to update
        status: New packing status (not_packed, packed, optional)
        notes: Optional updated notes
        
    Returns:
        Updated packing item
    """
    item = service.update_item_status(
        item_id=item_id,
        status=status,
        notes=notes
    )
    
    if not item:
        return {"error": f"Packing item with ID {item_id} not found"}
    
    return format_packing_item_response(item)


@mcp.tool()
def delete_item(item_id: int) -> Dict[str, Any]:
    """Delete an item from a packing list
    
    Args:
        item_id: ID of the item to delete
        
    Returns:
        Success status and message
    """
    success = service.delete_item(item_id)
    
    if success:
        return {
            "success": True,
            "message": f"Item {item_id} deleted successfully"
        }
    else:
        return {
            "success": False,
            "error": f"Item with ID {item_id} not found"
        }


@mcp.tool()
def export_to_markdown() -> Dict[str, Any]:
    """Export all packing lists to a markdown file
    
    Returns:
        Success status and file path of the exported markdown
    """
    try:
        file_path = service.export_to_markdown()
        return {
            "success": True,
            "message": "Packing lists exported to markdown successfully",
            "file_path": file_path
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to export to markdown: {str(e)}"
        }


# Resource for providing packing list data
@mcp.resource("packing-list://list/{list_id}")
def get_packing_list_resource(list_id: str) -> str:
    """Get a packing list as a resource"""
    try:
        list_id_int = int(list_id)
        packing_list = service.get_packing_list(list_id_int)
        
        if not packing_list:
            return f"Packing list {list_id} not found"
        
        # Format as readable text
        text = f"# {packing_list.name}\n\n"
        
        if packing_list.description:
            text += f"**Description:** {packing_list.description}\n\n"
        
        if packing_list.destination:
            text += f"**Destination:** {packing_list.destination}\n\n"
        
        if packing_list.travel_start_date or packing_list.travel_end_date:
            text += "**Travel Dates:** "
            if packing_list.travel_start_date:
                text += packing_list.travel_start_date.strftime("%Y-%m-%d")
            if packing_list.travel_end_date:
                text += f" to {packing_list.travel_end_date.strftime('%Y-%m-%d')}"
            text += "\n\n"
        
        completion = packing_list.get_completion_percentage()
        text += f"**Progress:** {packing_list.get_packed_count()}/{packing_list.get_total_count()} items packed ({completion:.1f}%)\n\n"
        
        if packing_list.items:
            text += "## Items\n\n"
            
            # Group by category
            categories = {}
            for item in packing_list.items:
                cat = item.category.value.replace('_', ' ').title()
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(item)
            
            for category, items in sorted(categories.items()):
                text += f"### {category}\n\n"
                
                for item in sorted(items, key=lambda x: (-x.priority, x.name)):
                    status_icon = "✅" if item.status.value == "packed" else ("⭕" if item.status.value == "optional" else "⬜")
                    priority_stars = "⭐" * item.priority if item.priority > 1 else ""
                    
                    text += f"- {status_icon} {item.name}"
                    if item.quantity > 1:
                        text += f" (x{item.quantity})"
                    if priority_stars:
                        text += f" {priority_stars}"
                    if item.notes:
                        text += f" - *{item.notes}*"
                    text += "\n"
                
                text += "\n"
        else:
            text += "*No items in this packing list yet.*\n"
        
        return text
        
    except ValueError:
        return f"Invalid list ID: {list_id}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
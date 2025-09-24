"""
Packing list persistence service - Markdown file operations for packing lists.
"""

import os
import re
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from config import STORAGE_PATH
from models import PackingList, PackingItem, PackingStatus, ItemCategory, PackingListSummary
from utils import (
    datetime_to_str, 
    str_to_datetime,
    validate_item_category,
    validate_packing_status
)


class PackingListService:
    """Service class for packing list operations using markdown-only storage"""
    
    def __init__(self):
        # Set up markdown file path
        db_dir = Path(STORAGE_PATH).parent
        self.markdown_file = db_dir / "persist-packing-list.md"
        self.next_list_id = 1
        self.next_item_id = 1
        self._ensure_file_exists()
        self._load_next_ids()
    
    def _ensure_file_exists(self):
        """Create the markdown file if it doesn't exist"""
        if not self.markdown_file.exists():
            self.markdown_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.markdown_file, 'w', encoding='utf-8') as f:
                f.write("# Travel Packing Lists\n\n*No packing lists created yet.*\n")
    
    def _load_next_ids(self):
        """Load the next available IDs from the markdown file"""
        try:
            with open(self.markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find highest list ID
            list_matches = re.findall(r'<!-- LIST_ID:(\d+) -->', content)
            if list_matches:
                self.next_list_id = max(int(m) for m in list_matches) + 1
            
            # Find highest item ID
            item_matches = re.findall(r'<!-- ITEM_ID:(\d+) -->', content)
            if item_matches:
                self.next_item_id = max(int(m) for m in item_matches) + 1
                
        except (FileNotFoundError, ValueError):
            pass
    
    def _parse_markdown_lists(self) -> List[PackingList]:
        """Parse packing lists from markdown file"""
        try:
            with open(self.markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            return []
        
        lists = []
        
        # Split by list sections (## headings)
        sections = re.split(r'^## ', content, flags=re.MULTILINE)
        
        for section in sections[1:]:  # Skip first part (header)
            if not section.strip():
                continue
                
            lines = section.split('\n')
            if not lines:
                continue
            
            # Extract list metadata
            list_id_match = re.search(r'<!-- LIST_ID:(\d+) -->', section)
            if not list_id_match:
                continue
            
            list_id = int(list_id_match.group(1))
            name = lines[0].strip()
            
            # Parse metadata
            description = None
            destination = None
            travel_start_date = None
            travel_end_date = None
            created_at = None
            updated_at = None
            
            for line in lines:
                if line.startswith('**Description:**'):
                    description = line.replace('**Description:**', '').strip()
                elif line.startswith('**Destination:**'):
                    destination = line.replace('**Destination:**', '').strip()
                elif line.startswith('**Travel Dates:**'):
                    date_part = line.replace('**Travel Dates:**', '').strip()
                    if ' to ' in date_part:
                        start_str, end_str = date_part.split(' to ', 1)
                        try:
                            travel_start_date = datetime.strptime(start_str.strip(), '%Y-%m-%d')
                            travel_end_date = datetime.strptime(end_str.strip(), '%Y-%m-%d')
                        except ValueError:
                            pass
                    else:
                        try:
                            travel_start_date = datetime.strptime(date_part.strip(), '%Y-%m-%d')
                        except ValueError:
                            pass
                elif line.startswith('**Created:**'):
                    created_str = line.replace('**Created:**', '').strip()
                    try:
                        created_at = datetime.strptime(created_str, '%Y-%m-%d at %H:%M')
                    except ValueError:
                        pass
            
            # Parse items
            items = []
            current_category = None
            
            for line in lines:
                # Category headers
                if line.startswith('#### '):
                    current_category = line.replace('####', '').strip().lower().replace(' ', '_')
                    continue
                
                # Item lines
                if line.startswith('- '):
                    item_match = re.search(r'<!-- ITEM_ID:(\d+) -->(.+)', line)
                    if item_match:
                        item_id = int(item_match.group(1))
                        item_content = item_match.group(2).strip()
                        
                        # Parse item details
                        status_icon = item_content[0] if item_content else '❌'
                        status = PackingStatus.PACKED if status_icon == '✅' else (
                            PackingStatus.OPTIONAL if status_icon == '⭕' else PackingStatus.NOT_PACKED
                        )
                        
                        # Extract name, quantity, priority, notes
                        item_text = item_content[2:].strip()  # Remove status icon
                        
                        # Extract name (bold part)
                        name_match = re.search(r'\*\*(.+?)\*\*', item_text)
                        item_name = name_match.group(1) if name_match else item_text
                        
                        # Extract quantity
                        quantity = 1
                        quantity_match = re.search(r'\*\(x(\d+)\)\*', item_text)
                        if quantity_match:
                            quantity = int(quantity_match.group(1))
                        
                        # Extract priority (stars)
                        priority = 1
                        star_match = re.search(r'(⭐+)', item_text)
                        if star_match:
                            priority = len(star_match.group(1)) + 1
                        
                        # Extract notes
                        notes = None
                        notes_match = re.search(r' - (.+)$', item_text)
                        if notes_match:
                            notes = notes_match.group(1).strip()
                        
                        item = PackingItem(
                            id=item_id,
                            name=item_name,
                            category=validate_item_category(current_category or 'miscellaneous'),
                            quantity=quantity,
                            status=status,
                            notes=notes,
                            priority=priority,
                            created_at=created_at,
                            updated_at=updated_at
                        )
                        items.append(item)
            
            packing_list = PackingList(
                id=list_id,
                name=name,
                description=description,
                destination=destination,
                travel_start_date=travel_start_date,
                travel_end_date=travel_end_date,
                items=items,
                created_at=created_at or datetime.now(),
                updated_at=updated_at or datetime.now()
            )
            lists.append(packing_list)
        
        return lists
    
    def _write_markdown_file(self, lists: List[PackingList]):
        """Write all packing lists to the markdown file"""
        content = "# Travel Packing Lists\n\n"
        content += f"*Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*\n\n"
        
        if not lists:
            content += "*No packing lists created yet.*\n"
        else:
            content += f"Total lists: {len(lists)}\n\n"
            content += "---\n\n"
            
            for packing_list in lists:
                content += self._format_list_as_markdown(packing_list)
                content += "\n---\n\n"
        
        with open(self.markdown_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _format_list_as_markdown(self, packing_list: PackingList) -> str:
        """Format a single packing list as markdown with embedded IDs"""
        text = f"## {packing_list.name} <!-- LIST_ID:{packing_list.id} -->\n\n"
        
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
        
        if packing_list.created_at:
            text += f"**Created:** {packing_list.created_at.strftime('%Y-%m-%d at %H:%M')}\n\n"
        
        if packing_list.items:
            text += "### Items\n\n"
            
            # Group by category
            categories = {}
            for item in packing_list.items:
                cat = item.category.value.replace('_', ' ').title()
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(item)
            
            for category, items in sorted(categories.items()):
                text += f"#### {category}\n\n"
                
                for item in sorted(items, key=lambda x: (-x.priority, x.name)):
                    status_icon = "✅" if item.status.value == "packed" else ("⭕" if item.status.value == "optional" else "❌")
                    priority_stars = "⭐" * item.priority if item.priority > 1 else ""
                    
                    text += f"- {status_icon} **{item.name}**"
                    if item.quantity > 1:
                        text += f" *(x{item.quantity})*"
                    if priority_stars:
                        text += f" {priority_stars}"
                    if item.notes:
                        text += f" - {item.notes}"
                    text += f" <!-- ITEM_ID:{item.id} -->\n"
                
                text += "\n"
        else:
            text += "*No items in this packing list yet.*\n\n"
        
        return text
    
    def create_packing_list(
        self,
        name: str,
        description: Optional[str] = None,
        destination: Optional[str] = None,
        travel_start_date: Optional[datetime] = None,
        travel_end_date: Optional[datetime] = None
    ) -> PackingList:
        """Create a new packing list"""
        lists = self._parse_markdown_lists()
        now = datetime.now()
        
        new_list = PackingList(
            id=self.next_list_id,
            name=name,
            description=description,
            destination=destination,
            travel_start_date=travel_start_date,
            travel_end_date=travel_end_date,
            items=[],
            created_at=now,
            updated_at=now
        )
        
        lists.append(new_list)
        self.next_list_id += 1
        self._write_markdown_file(lists)
        
        return new_list
    
    def get_packing_list(self, list_id: int) -> Optional[PackingList]:
        """Get a packing list by ID"""
        lists = self._parse_markdown_lists()
        for plist in lists:
            if plist.id == list_id:
                return plist
        return None
    
    def update_packing_list(
        self,
        list_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        destination: Optional[str] = None,
        travel_start_date: Optional[datetime] = None,
        travel_end_date: Optional[datetime] = None
    ) -> Optional[PackingList]:
        """Update an existing packing list"""
        lists = self._parse_markdown_lists()
        
        for plist in lists:
            if plist.id == list_id:
                now = datetime.now()
                
                if name is not None:
                    plist.name = name
                if description is not None:
                    plist.description = description
                if destination is not None:
                    plist.destination = destination
                if travel_start_date is not None:
                    plist.travel_start_date = travel_start_date
                if travel_end_date is not None:
                    plist.travel_end_date = travel_end_date
                
                plist.updated_at = now
                self._write_markdown_file(lists)
                return plist
        
        return None
    
    def delete_packing_list(self, list_id: int) -> bool:
        """Delete a packing list"""
        lists = self._parse_markdown_lists()
        
        for i, plist in enumerate(lists):
            if plist.id == list_id:
                del lists[i]
                self._write_markdown_file(lists)
                return True
        
        return False
    
    def list_packing_lists(self) -> List[PackingListSummary]:
        """Get all packing lists with summary information"""
        lists = self._parse_markdown_lists()
        summaries = []
        
        for plist in lists:
            total_items = len([item for item in plist.items if item.status != PackingStatus.OPTIONAL])
            packed_items = len([item for item in plist.items if item.status == PackingStatus.PACKED])
            completion = (packed_items / total_items * 100) if total_items > 0 else 0
            
            summary = PackingListSummary(
                id=plist.id,
                name=plist.name,
                destination=plist.destination,
                travel_start_date=plist.travel_start_date,
                item_count=len(plist.items),
                packed_count=packed_items,
                completion_percentage=completion,
                created_at=plist.created_at,
                updated_at=plist.updated_at
            )
            summaries.append(summary)
        
        return sorted(summaries, key=lambda x: x.updated_at or datetime.min, reverse=True)
    
    def add_item_to_list(
        self,
        list_id: int,
        name: str,
        category: str = "miscellaneous",
        quantity: int = 1,
        status: str = "not_packed",
        notes: Optional[str] = None,
        priority: int = 1
    ) -> Optional[PackingItem]:
        """Add an item to a packing list"""
        lists = self._parse_markdown_lists()
        
        for plist in lists:
            if plist.id == list_id:
                now = datetime.now()
                
                new_item = PackingItem(
                    id=self.next_item_id,
                    name=name,
                    category=validate_item_category(category),
                    quantity=quantity,
                    status=validate_packing_status(status),
                    notes=notes,
                    priority=priority,
                    created_at=now,
                    updated_at=now
                )
                
                plist.items.append(new_item)
                plist.updated_at = now
                self.next_item_id += 1
                self._write_markdown_file(lists)
                
                return new_item
        
        return None
    
    def update_item_status(
        self,
        item_id: int,
        status: str,
        notes: Optional[str] = None
    ) -> Optional[PackingItem]:
        """Update an item's packing status"""
        lists = self._parse_markdown_lists()
        
        for plist in lists:
            for item in plist.items:
                if item.id == item_id:
                    now = datetime.now()
                    item.status = validate_packing_status(status)
                    if notes is not None:
                        item.notes = notes
                    item.updated_at = now
                    plist.updated_at = now
                    self._write_markdown_file(lists)
                    return item
        
        return None
    
    def delete_item(self, item_id: int) -> bool:
        """Delete an item from a packing list"""
        lists = self._parse_markdown_lists()
        
        for plist in lists:
            for i, item in enumerate(plist.items):
                if item.id == item_id:
                    del plist.items[i]
                    plist.updated_at = datetime.now()
                    self._write_markdown_file(lists)
                    return True
        
        return False
    
    def export_to_markdown(self) -> str:
        """Manually trigger export to markdown and return the file path"""
        lists = self._parse_markdown_lists()
        self._write_markdown_file(lists)
        return str(self.markdown_file)
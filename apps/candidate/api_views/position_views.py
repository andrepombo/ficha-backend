from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from django.conf import settings
import json
import os


class PositionViewSet(viewsets.ViewSet):
    """
    ViewSet for managing available positions.
    Stores positions in a JSON file.
    """
    
    POSITIONS_FILE = os.path.join(settings.BASE_DIR, 'positions.json')
    
    def _read_positions(self):
        """Read positions from file."""
        if os.path.exists(self.POSITIONS_FILE):
            try:
                with open(self.POSITIONS_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading positions: {e}")
        return []
    
    def _write_positions(self, positions):
        """Write positions to file."""
        try:
            with open(self.POSITIONS_FILE, 'w') as f:
                json.dump(positions, f, indent=2)
        except Exception as e:
            print(f"Error writing positions: {e}")
    
    def get_permissions(self):
        """Allow public access for list, admin for modifications."""
        if self.action in ['list', 'initialize_defaults']:
            return [AllowAny()]
        return [IsAdminUser()]
    
    def list(self, request):
        """Get all active positions."""
        positions = self._read_positions()
        # Filter only active positions for public
        if not request.user.is_staff:
            positions = [p for p in positions if p.get('is_active', True)]
        return Response(positions)
    
    def create(self, request):
        """Create a new position."""
        positions = self._read_positions()
        
        # Generate new ID
        max_id = max([p.get('id', 0) for p in positions], default=0)
        new_position = {
            'id': max_id + 1,
            'name': request.data.get('name'),
            'is_active': request.data.get('is_active', True),
            'created_at': request.data.get('created_at'),
        }
        
        positions.append(new_position)
        self._write_positions(positions)
        
        return Response(new_position, status=status.HTTP_201_CREATED)
    
    def update(self, request, pk=None):
        """Update a position."""
        positions = self._read_positions()
        
        for i, pos in enumerate(positions):
            if pos['id'] == int(pk):
                positions[i].update(request.data)
                self._write_positions(positions)
                return Response(positions[i])
        
        return Response({'error': 'Position not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def destroy(self, request, pk=None):
        """Delete a position."""
        positions = self._read_positions()
        positions = [p for p in positions if p['id'] != int(pk)]
        self._write_positions(positions)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update all positions."""
        positions = request.data.get('positions', [])
        self._write_positions(positions)
        return Response({'status': 'updated', 'count': len(positions)})
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def initialize_defaults(self, request):
        """Initialize with default positions if none exist."""
        existing = self._read_positions()
        if not existing:
            defaults = [
                {'id': 1, 'name': 'Pintor', 'is_active': True, 'created_at': '2025-01-15T00:00:00Z'},
                {'id': 2, 'name': 'Auxiliar de Pintor', 'is_active': True, 'created_at': '2025-01-15T00:00:00Z'},
                {'id': 3, 'name': 'Encarregado de Pintura', 'is_active': True, 'created_at': '2025-01-15T00:00:00Z'},
            ]
            self._write_positions(defaults)
            return Response({'status': 'initialized', 'positions': defaults})
        return Response({'status': 'already_exists', 'positions': existing})

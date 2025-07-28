# shops/permissions.py
from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow users with the 'OWNER' role.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated or not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.role == 'OWNER'

# --- GANTI IsOwnerOrStaffOfShop DENGAN CLASS BARU INI ---
class IsShopMember(permissions.BasePermission):
    """
    Allows access only to the owner or staff of the shop specified in the URL.
    Handles both 'pk' and 'shop_pk' from URL.
    """
    def has_permission(self, request, view):
        # Coba dapatkan ID toko dari URL, baik 'pk' maupun 'shop_pk'
        shop_id_from_url = view.kwargs.get('pk') or view.kwargs.get('shop_pk')
        if not shop_id_from_url:
            return False # Tidak bisa menentukan toko dari URL

        user = request.user
        if not user or not user.is_authenticated or not hasattr(user, 'profile') or not user.profile.coffee_shop:
            return False # User tidak valid atau tidak terhubung ke toko manapun

        # Izinkan akses hanya jika ID toko user sama dengan ID toko di URL
        return user.profile.coffee_shop.id == shop_id_from_url
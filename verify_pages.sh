#!/bin/bash
# Verify all pages are working and showing data

echo "========================================"
echo "VERIFYING ALL PAGES ARE WORKING"
echo "========================================"

# Test each page
pages=(
    "/ Dashboard"
    "/inventory Inventory"
    "/recipes Recipes"
    "/menu_items Menu_Items"
    "/menus_mgmt Menus_Management"
    "/pricing-analysis Pricing_Analysis"
)

all_pass=true

for page_info in "${pages[@]}"; do
    url=$(echo $page_info | cut -d' ' -f1)
    name=$(echo $page_info | cut -d' ' -f2)
    
    echo -e "\nTesting $name page ($url)..."
    
    # Check if page loads (200 OK)
    status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8888$url)
    if [ "$status" = "200" ]; then
        echo "✓ Page loads successfully (HTTP 200)"
        
        # Check for error messages
        if curl -s http://localhost:8888$url | grep -q "Server Error\|Traceback\|Exception"; then
            echo "✗ Page contains error messages"
            all_pass=false
        else
            echo "✓ No error messages found"
            
            # Check for empty states
            if [ "$name" != "Dashboard" ]; then
                if curl -s http://localhost:8888$url | grep -q "No .* yet\|No .* found\|empty"; then
                    echo "⚠ Page might be showing empty state"
                    # Extract what's empty
                    curl -s http://localhost:8888$url | grep -o "No .* yet\|No .* found" | head -1
                else
                    echo "✓ Page appears to have data"
                fi
            fi
        fi
    else
        echo "✗ Page failed to load (HTTP $status)"
        all_pass=false
    fi
done

echo -e "\n========================================"
if [ "$all_pass" = true ]; then
    echo "✓ ALL PAGES ARE WORKING!"
else
    echo "✗ SOME PAGES HAVE ISSUES"
fi
echo "========================================"

# Check database stats
echo -e "\nDatabase Statistics:"
sqlite3 restaurant_calculator.db "
SELECT 'Inventory Items:' as label, COUNT(*) as count FROM inventory
UNION ALL SELECT 'Recipes:' as label, COUNT(*) FROM recipes
UNION ALL SELECT 'Menu Items:' as label, COUNT(*) FROM menu_items
UNION ALL SELECT 'Menus:' as label, COUNT(*) FROM menus
UNION ALL SELECT 'Menu Assignments:' as label, COUNT(*) FROM menu_menu_items;"
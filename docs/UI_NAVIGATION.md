# UI and Navigation Guide

This guide covers the user interface improvements and navigation system in Postfix Manager.

## Table of Contents

- [Breadcrumb System](#breadcrumb-system)
- [Navigation Utilities](#navigation-utilities)
- [Login Page Enhancements](#login-page-enhancements)
- [Template System](#template-system)
- [Theme Management](#theme-management)

## Breadcrumb System

### Overview

Postfix Manager features a dual-layer breadcrumb system that provides both automatic and programmatic navigation:

1. **Automatic Path-based Breadcrumbs**: Generated from URL paths when no custom breadcrumbs are set
2. **Programmatic Breadcrumbs**: Custom breadcrumbs set by routes for better user experience

### How It Works

The system automatically detects which breadcrumb system to use:

```python
# Template context processor automatically checks for programmatic breadcrumbs first
def get_breadcrumbs():
    # First check if programmatic breadcrumbs are set
    from app.utils.navigation import get_breadcrumbs as get_programmatic_breadcrumbs
    programmatic_breadcrumbs = get_programmatic_breadcrumbs()
    
    if programmatic_breadcrumbs:
        # Use custom breadcrumbs
        return [(crumb.text, crumb.url) for crumb in programmatic_breadcrumbs]
    
    # Fall back to automatic path-based breadcrumbs
    # ... automatic generation logic
```

### Breadcrumb Patterns

#### Mail Management
```python
set_mail_breadcrumbs('Postfix', request.path)
# Results in: Home > Mail Management > Postfix
```

#### Dashboard
```python
set_dashboard_breadcrumbs('Domains', request.path)
# Results in: Home > Dashboard > Domains
```

#### LDAP Management
```python
set_ldap_breadcrumbs('Directory Browser', request.path)
# Results in: Home > LDAP Management > Directory Browser
```

### Implementation in Routes

```python
from app.utils.navigation import set_mail_breadcrumbs, set_dashboard_breadcrumbs

@bp.route('/postfix')
@login_required
def postfix():
    set_mail_breadcrumbs('Postfix', request.path)
    return render_template('modules/mail/postfix.html')

@bp.route('/domains')
@login_required
def domains():
    set_dashboard_breadcrumbs('Domains', request.path)
    return render_template('modules/dashboard/domains.html')
```

## Navigation Utilities

### Core Functions

- `set_breadcrumbs(breadcrumbs)`: Set custom breadcrumbs for current request
- `get_breadcrumbs()`: Get current breadcrumbs
- `add_breadcrumb(text, url, active=False)`: Add single breadcrumb
- `clear_breadcrumbs()`: Clear all breadcrumbs
- `get_page_title()`: Get page title from breadcrumbs

### Module-specific Functions

- `set_mail_breadcrumbs(subsection, current_path)`
- `set_dashboard_breadcrumbs(subsection, current_path)`
- `set_ldap_breadcrumbs(subsection, current_path)`
- `set_system_breadcrumbs(subsection, current_path)`

### Navigation Context

```python
def get_navigation_context():
    return {
        'breadcrumbs': get_breadcrumbs(),
        'page_title': get_page_title(),
        'current_path': request.path,
        'current_module': get_current_module()
    }
```

## Login Page Enhancements

### Minimal Navbar

The login page now features a clean, minimal navbar that includes:

- **App Branding**: "Postfix Manager" displayed prominently
- **Theme Toggle**: Dark/light mode switch accessible before login
- **Seamless Integration**: No background colors or borders

### Design Features

- **Absolute Positioning**: Navbar doesn't interfere with page layout
- **Transparent Background**: Blends seamlessly with page content
- **Responsive Design**: Works on all device sizes
- **Theme Persistence**: User preference saved in localStorage

### Implementation

```html
<!-- Minimal Navbar for Login/Auth Pages -->
<nav class="absolute top-0 left-0 right-0 z-10 p-4">
  <div class="flex items-center justify-between">
    <!-- App Name -->
    <div class="flex items-center">
      <h1 class="text-xl font-bold text-gray-900 dark:text-white">
        Postfix Manager
      </h1>
    </div>
    
    <!-- Theme Toggle -->
    <button id="theme-toggle" type="button" class="...">
      <!-- Sun/Moon icons -->
    </button>
  </div>
</nav>
```

## Template System

### Template Hierarchy

- `base.html`: Full application template with complete navbar
- `simple.html`: Minimal template for auth pages with minimal navbar
- Module templates: Extend appropriate base template

### Context Processors

The template system includes several context processors:

- **Global Variables**: `current_year`, `app_name`, `current_user`
- **Navigation Utilities**: `get_breadcrumbs()`, `is_active_route()`, `get_nav_class()`
- **Request Context**: User ID, session ID for logging

### Breadcrumb Rendering

```html
{% set breadcrumbs = get_breadcrumbs() %}
{% if breadcrumbs %}
  {% for breadcrumb in breadcrumbs %}
    <li>
      <div class="flex items-center">
        <svg class="w-4 h-4 text-gray-400">...</svg>
        <a href="{{ breadcrumb[1] }}" class="...">{{ breadcrumb[0] }}</a>
      </div>
    </li>
  {% endfor %}
{% endif %}
```

## Theme Management

### Dark/Light Mode Toggle

The theme system provides:

- **Automatic Detection**: Detects user's system preference
- **Manual Override**: Users can manually toggle themes
- **Persistence**: Theme choice saved in localStorage
- **Smooth Transitions**: Icons smoothly transition between states

### Theme Implementation

```javascript
function setTheme(theme) {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
  localStorage.setItem('theme', theme);
  updateIcons();
}
```

### CSS Classes

The theme system uses Tailwind CSS dark mode classes:

- `dark:bg-gray-900`: Dark background
- `dark:text-white`: Dark text
- `dark:border-gray-700`: Dark borders
- `dark:hover:bg-gray-700`: Dark hover states

## Best Practices

### Setting Breadcrumbs

1. **Always pass current_path**: Use `request.path` for accurate URLs
2. **Use descriptive subsection names**: Make breadcrumbs user-friendly
3. **Set breadcrumbs early**: Set them at the beginning of route functions
4. **Consistent naming**: Use consistent patterns across modules

### Template Usage

1. **Extend appropriate base**: Use `simple.html` for auth pages, `base.html` for main app
2. **Account for navbar**: Add top padding when using minimal navbar
3. **Use context processors**: Leverage built-in navigation utilities
4. **Responsive design**: Ensure breadcrumbs work on all screen sizes

### Theme Considerations

1. **Test both themes**: Verify UI works in both light and dark modes
2. **Consistent contrast**: Maintain readability across themes
3. **Smooth transitions**: Use CSS transitions for theme changes
4. **Accessibility**: Ensure theme toggle is keyboard accessible

## Troubleshooting

### Common Issues

1. **Breadcrumbs not showing**: Check if `set_breadcrumbs()` is called
2. **Wrong breadcrumb URLs**: Ensure `current_path` is passed correctly
3. **Theme not persisting**: Check localStorage and JavaScript errors
4. **Navbar overlap**: Verify top padding is sufficient for content

### Debug Commands

```bash
# Test breadcrumb system
python3 -c "from app import create_app; app = create_app(); print('✅ App created successfully')"

# Check template rendering
python3 -c "from app.extensions.templates import init_template_context; print('✅ Templates initialized')"
```

## Future Enhancements

- **Breadcrumb History**: Track user navigation paths
- **Custom Breadcrumb Styles**: Allow modules to customize appearance
- **Advanced Theme Options**: Multiple color schemes and customization
- **Navigation Analytics**: Track user navigation patterns

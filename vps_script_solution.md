# VPS Script Solution для SAMO API

## Решение через прямой вызов скрипта на VPS

Поскольку у вас есть возможность вызывать скрипты на VPS сервере, создадим простое решение:

### 1. Создать скрипт на VPS

Создайте файл на вашем VPS `/home/scripts/samo_proxy.php`:

```php
<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] == 'OPTIONS') {
    exit(0);
}

// SAMO API configuration
$samo_url = 'https://booking.crystalbay.com/export/default.php';
$oauth_token = '27bd59a7ac67422189789f0188167379';

// Get parameters from request
$action = $_REQUEST['action'] ?? 'SearchTour_TOWNFROMS';
$extra_params = $_REQUEST['params'] ?? '';

// Build SAMO API parameters
$params = [
    'samo_action' => 'api',
    'version' => '1.0', 
    'type' => 'json',
    'action' => $action,
    'oauth_token' => $oauth_token
];

// Add extra parameters if provided (as JSON string)
if ($extra_params && is_string($extra_params)) {
    $decoded = json_decode($extra_params, true);
    if ($decoded) {
        $params = array_merge($params, $decoded);
    }
}

// Make request to SAMO API
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $samo_url);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($params));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 30);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'User-Agent: Crystal Bay Travel Integration/1.0',
    'Accept: application/json',
    'Content-Type: application/x-www-form-urlencoded'
]);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$error = curl_error($ch);
curl_close($ch);

// Return response
if ($error) {
    echo json_encode(['error' => 'cURL error: ' . $error]);
} else {
    // Return raw response from SAMO API
    echo $response;
}
?>
```

### 2. Простой bash скрипт (альтернатива)

Создайте `/home/scripts/samo_api.sh`:

```bash
#!/bin/bash

ACTION=${1:-"SearchTour_TOWNFROMS"}
EXTRA_PARAMS=${2:-""}

# SAMO API endpoint
SAMO_URL="https://booking.crystalbay.com/export/default.php"
OAUTH_TOKEN="27bd59a7ac67422189789f0188167379"

# Build parameters
PARAMS="samo_action=api&version=1.0&type=json&action=${ACTION}&oauth_token=${OAUTH_TOKEN}"

# Add extra parameters if provided
if [ ! -z "$EXTRA_PARAMS" ]; then
    PARAMS="${PARAMS}&${EXTRA_PARAMS}"
fi

# Make request
curl -X POST "${SAMO_URL}" \
    -H "User-Agent: Crystal Bay Travel Integration/1.0" \
    -H "Accept: application/json" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "${PARAMS}" \
    --max-time 30

echo ""
```

Сделать исполняемым:
```bash
chmod +x /home/scripts/samo_api.sh
```

### 3. Тест скриптов

Тест PHP скрипта:
```bash
php /home/scripts/samo_proxy.php action=SearchTour_TOWNFROMS
```

Тест bash скрипта:
```bash
/home/scripts/samo_api.sh SearchTour_TOWNFROMS
```

### 4. Web-доступ к PHP скрипту

Если есть веб-сервер, поместите скрипт в `/var/www/html/samo_proxy.php`

Тогда можно вызывать:
```
http://your-vps-ip/samo_proxy.php?action=SearchTour_TOWNFROMS
```

## Интеграция в Replit

Обновлю VPS proxy client для вызова скриптов через SSH или HTTP.
<?php
class DatabaseConfig {
    private $host;
    private $username;
    private $password;
    private $database;
    private $port;
    
    public function __construct() {
        $this->host = getenv('DB_HOST') ?: 'localhost';
        $this->username = getenv('DB_USERNAME') ?: 'root';
        $this->password = getenv('DB_PASSWORD') ?: '';
        $this->database = getenv('DB_NAME') ?: 'testdb';
        $this->port = getenv('DB_PORT') ?: '3306';
    }
    
    public function getConnection() {
        try {
            $dsn = "mysql:host={$this->host};port={$this->port};dbname={$this->database};charset=utf8mb4";
            $pdo = new PDO($dsn, $this->username, $this->password);
            $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            return $pdo;
        } catch(PDOException $e) {
            throw new Exception("Connection failed: " . $e->getMessage());
        }
    }
}

// API endpoint handler
function handleApiRequest() {
    header('Content-Type: application/json');
    
    $request_uri = $_SERVER['REQUEST_URI'];
    $path = parse_url($request_uri, PHP_URL_PATH);
    $method = $_SERVER['REQUEST_METHOD'];
    
    // Health check endpoint
    if ($path === '/api/health' && $method === 'GET') {
        http_response_code(200);
        echo json_encode([
            'status' => 'success',
            'message' => 'Application is running',
            'timestamp' => date('Y-m-d H:i:s'),
            'php_version' => PHP_VERSION,
            'server_time' => date('Y-m-d H:i:s'),
            'environment' => getenv('APP_ENV') ?: 'production'
        ]);
        exit;
    }
    
    // Database connection test endpoint
    if ($path === '/api/db-test' && $method === 'GET') {
        try {
            $dbConfig = new DatabaseConfig();
            $pdo = $dbConfig->getConnection();
            
            // Test database connection with a simple query
            $stmt = $pdo->query("SELECT 1 as test, NOW() as current_time");
            $result = $stmt->fetch(PDO::FETCH_ASSOC);
            
            http_response_code(200);
            echo json_encode([
                'status' => 'success',
                'message' => 'Database connection successful',
                'database_time' => $result['current_time'],
                'connection_test' => $result['test'] == 1 ? 'passed' : 'failed',
                'host' => getenv('DB_HOST') ?: 'localhost',
                'database' => getenv('DB_NAME') ?: 'testdb',
                'timestamp' => date('Y-m-d H:i:s')
            ]);
        } catch (Exception $e) {
            http_response_code(500);
            echo json_encode([
                'status' => 'error',
                'message' => 'Database connection failed',
                'error' => $e->getMessage(),
                'timestamp' => date('Y-m-d H:i:s')
            ]);
        }
        exit;
    }
    
    // Database status endpoint with more details
    if ($path === '/api/db-status' && $method === 'GET') {
        try {
            $dbConfig = new DatabaseConfig();
            $pdo = $dbConfig->getConnection();
            
            // Get database version
            $versionStmt = $pdo->query("SELECT VERSION() as version");
            $version = $versionStmt->fetch(PDO::FETCH_ASSOC)['version'];
            
            // Check if test table exists
            $tableCheckStmt = $pdo->query("SHOW TABLES LIKE 'test'");
            $tableExists = $tableCheckStmt->rowCount() > 0;
            
            $response = [
                'status' => 'success',
                'message' => 'Database status retrieved successfully',
                'database_version' => $version,
                'test_table_exists' => $tableExists,
                'connection_details' => [
                    'host' => getenv('DB_HOST') ?: 'localhost',
                    'database' => getenv('DB_NAME') ?: 'testdb',
                    'port' => getenv('DB_PORT') ?: '3306'
                ],
                'timestamp' => date('Y-m-d H:i:s')
            ];
            
            // If test table exists, get record count
            if ($tableExists) {
                $countStmt = $pdo->query("SELECT COUNT(*) as count FROM test");
                $count = $countStmt->fetch(PDO::FETCH_ASSOC)['count'];
                $response['test_table_records'] = (int)$count;
            }
            
            http_response_code(200);
            echo json_encode($response);
        } catch (Exception $e) {
            http_response_code(500);
            echo json_encode([
                'status' => 'error',
                'message' => 'Failed to retrieve database status',
                'error' => $e->getMessage(),
                'timestamp' => date('Y-m-d H:i:s')
            ]);
        }
        exit;
    }
    
    // If no matching endpoint, return 404
    http_response_code(404);
    echo json_encode([
        'status' => 'error',
        'message' => 'API endpoint not found',
        'requested_path' => $path,
        'method' => $method,
        'available_endpoints' => [
            'GET /api/health' => 'Application health check',
            'GET /api/db-test' => 'Database connection test',
            'GET /api/db-status' => 'Detailed database status',
            'POST /api/create-test-data' => 'Create sample test data'
        ],
        'timestamp' => date('Y-m-d H:i:s')
    ]);
    exit;
}

// Handle API requests if path starts with /api/
if (isset($_SERVER['REQUEST_URI']) && strpos($_SERVER['REQUEST_URI'], '/api/') === 0) {
    handleApiRequest();
}
?>
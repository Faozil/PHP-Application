<?php
require_once 'config.php';

// Set default content type
header('Content-Type: text/html; charset=utf-8');

// Handle API requests first (This is configured in config.php but I included it here for clarity)
if (isset($_SERVER['REQUEST_URI']) && strpos($_SERVER['REQUEST_URI'], '/api/') === 0) {
    // API requests are handled in config.php
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple PHP MySQL App</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background-color: #f8f9fa;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .status { 
            padding: 10px; 
            margin: 10px 0; 
            border-radius: 4px; 
            border-left: 4px solid;
        }
        .success { 
            background-color: #d4edda; 
            color: #155724; 
            border-left-color: #28a745;
        }
        .error { 
            background-color: #f8d7da; 
            color: #721c24; 
            border-left-color: #dc3545;
        }
        .info { 
            background-color: #d1ecf1; 
            color: #0c5460; 
            border-left-color: #17a2b8;
        }
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 20px; 
        }
        th, td { 
            border: 1px solid #ddd; 
            padding: 12px; 
            text-align: left; 
        }
        th { 
            background-color: #f2f2f2; 
            font-weight: bold;
        }
        .env-info {
            margin-top: 40px; 
            padding-top: 20px; 
            border-top: 1px solid #ddd; 
            color: #666;
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 4px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1> Simple PHP Application</h1>
        
        <?php
        $dbConnected = false;
        $dbError = '';
        $tableExists = false;
        $recordCount = 0;
        $dbVersion = '';
        
        try {
            $dbConfig = new DatabaseConfig();
            $pdo = $dbConfig->getConnection();
            $dbConnected = true;
            
            echo '<div class="status success"> Database connection successful!</div>';
            
            // Get database version
            try {
                $versionStmt = $pdo->query("SELECT VERSION() as version");
                $versionResult = $versionStmt->fetch(PDO::FETCH_ASSOC);
                $dbVersion = $versionResult['version'];
            } catch (Exception $e) {
                $dbVersion = 'Unknown';
            }
            
            // Create test table if it doesn't exist
            $createTable = "CREATE TABLE IF NOT EXISTS test (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                value VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )";
            $pdo->exec($createTable);
            $tableExists = true;
            
            // Check if table has data
            $countStmt = $pdo->query("SELECT COUNT(*) as count FROM test");
            $countResult = $countStmt->fetch(PDO::FETCH_ASSOC);
            $recordCount = (int)$countResult['count'];
            
            // Insert sample data if table is empty
            if ($recordCount == 0) {
                $sampleData = [
                    ['Sample Item 1', 'This is a test value 1'],
                    ['Sample Item 2', 'This is a test value 2'],
                    ['Sample Item 3', 'This is a test value 3']
                ];
                
                $insertStmt = $pdo->prepare("INSERT INTO test (name, value) VALUES (?, ?)");
                foreach ($sampleData as $data) {
                    $insertStmt->execute($data);
                }
                
                // Update record count
                $countStmt = $pdo->query("SELECT COUNT(*) as count FROM test");
                $countResult = $countStmt->fetch(PDO::FETCH_ASSOC);
                $recordCount = (int)$countResult['count'];
                
                echo '<div class="status success"> Sample data inserted successfully!</div>';
            }
            
        } catch (Exception $e) {
            $dbError = $e->getMessage();
            echo '<div class="status error"> Database Error: ' . htmlspecialchars($dbError) . '</div>';
        }
        ?>

        <!-- Data Display -->
        <?php
        if ($dbConnected && $tableExists && $recordCount > 0) {
            try {
                // Fetch and display data
                $stmt = $pdo->query("SELECT * FROM test ORDER BY id LIMIT 10");
                $results = $stmt->fetchAll(PDO::FETCH_ASSOC);
                
                if (count($results) > 0) {
                    echo '<h2>Test Table Contents</h2>';
                    echo '<div class="status info">Showing latest ' . count($results) . ' records</div>';
                    echo '<table>';
                    echo '<thead><tr><th>ID</th><th>Name</th><th>Value</th><th>Created At</th></tr></thead>';
                    echo '<tbody>';
                    
                    foreach ($results as $row) {
                        echo '<tr>';
                        echo '<td>' . htmlspecialchars($row['id']) . '</td>';
                        echo '<td>' . htmlspecialchars($row['name']) . '</td>';
                        echo '<td>' . htmlspecialchars($row['value']) . '</td>';
                        echo '<td>' . htmlspecialchars($row['created_at']) . '</td>';
                        echo '</tr>';
                    }
                    
                    echo '</tbody></table>';
                }
            } catch (Exception $e) {
                echo '<div class="status error"> Error fetching data: ' . htmlspecialchars($e->getMessage()) . '</div>';
            }
        } elseif ($dbConnected && $tableExists && $recordCount == 0) {
            echo '<div class="status info"> Test table exists but contains no data. </div>';
        }
        ?>

        <!-- Environment Information -->
        <div class="env-info">
            <h3> Environment Information</h3>
            <div class="stats-grid">
                <div>
                    <strong>PHP Version:</strong><br>
                    <?php echo PHP_VERSION; ?>
                </div>
                <div>
                    <strong>Server Time:</strong><br>
                    <?php echo date('Y-m-d H:i:s T'); ?>
                </div>
                <div>
                    <strong>Environment:</strong><br>
                    <?php echo getenv('APP_ENV') ?: 'production'; ?>
                </div>
                <div>
                    <strong>Database Host:</strong><br>
                    <?php echo getenv('DB_HOST') ?: 'localhost'; ?>
                </div>
            </div>
            
            <?php if ($dbConnected): ?>
            <div style="margin-top: 15px;">
                <strong>Database Information:</strong><br>
                Version: <?php echo htmlspecialchars($dbVersion); ?><br>
                Database: <?php echo htmlspecialchars(getenv('DB_NAME') ?: 'testdb'); ?><br>
                Connection Status:  Active<br>
                Test Table: <?php echo $tableExists ? 'Exists' : 'Missing'; ?><br>
                Record Count: <?php echo $recordCount; ?>
            </div>
            <?php else: ?>
            <div style="margin-top: 15px;">
                <strong>Database Information:</strong><br>
                Connection Status: Failed<br>
                Error: <?php echo htmlspecialchars($dbError); ?>
            </div>
            <?php endif; ?>
        </div>

    </div>
</body>
</html>
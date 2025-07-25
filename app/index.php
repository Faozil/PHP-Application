<?php
require_once 'config.php';

header('Content-Type: text/html; charset=utf-8');
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple PHP MySQL App</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { background-color: #d4edda; color: #155724; }
        .error { background-color: #f8d7da; color: #721c24; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Simple PHP Application</h1>
        
        <?php
        try {
            $dbConfig = new DatabaseConfig();
            $pdo = $dbConfig->getConnection();
            
            echo '<div class="status success"> Database connection successful!</div>';
            
            // Create test table if it doesn't exist
            $createTable = "CREATE TABLE IF NOT EXISTS test (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                value VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )";
            $pdo->exec($createTable);
            
            // Insert sample data if table is empty
            $countStmt = $pdo->query("SELECT COUNT(*) FROM test");
            $count = $countStmt->fetchColumn();
            
            if ($count == 0) {
                $sampleData = [
                    ['Sample Item 1', 'This is a test value 1'],
                    ['Sample Item 2', 'This is a test value 2'],
                    ['Sample Item 3', 'This is a test value 3']
                ];
                
                $insertStmt = $pdo->prepare("INSERT INTO test (name, value) VALUES (?, ?)");
                foreach ($sampleData as $data) {
                    $insertStmt->execute($data);
                }
                echo '<div class="status success">✓ Sample data inserted!</div>';
            }
            
            // Fetch and display data
            $stmt = $pdo->query("SELECT * FROM test ORDER BY id");
            $results = $stmt->fetchAll(PDO::FETCH_ASSOC);
            
            if (count($results) > 0) {
                echo '<h2>Test Table Contents:</h2>';
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
                echo '<p><strong>Total records:</strong> ' . count($results) . '</p>';
            } else {
                echo '<div class="status error">No data found in test table.</div>';
            }
            
        } catch (Exception $e) {
            echo '<div class="status error">✗ Error: ' . htmlspecialchars($e->getMessage()) . '</div>';
        }
        ?>
        
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
            <p><strong>Environment Info:</strong></p>
            <p>PHP Version: <?php echo PHP_VERSION; ?></p>
            <p>Server Time: <?php echo date('Y-m-d H:i:s'); ?></p>
        </div>
    </div>
</body>
</html>

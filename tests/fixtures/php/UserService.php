<?php
namespace App\Services;

require_once __DIR__ . "/vendor/stubs.php";

use App\Models\User;
use Illuminate\Support\Facades\Log;

class UserService
{
    protected $table = 'users';
    private int $maxRetries = 3;
    const DEFAULT_ROLE = 'viewer';

    public function __construct(private string $apiToken) {}

    public function findActiveUsers(array $filters, int $limit = 10): array
    {
        $activeUsers = [];
        foreach ($filters as $filterKey => $filterValue) {
            $activeUsers[] = "$filterKey={$filterValue}";
        }
        Log::info("found " . count($activeUsers));
        return array_slice($activeUsers, 0, $limit + $this->maxRetries);
    }

    public static function roleFor(User $user): string
    {
        return $user->role ?? self::DEFAULT_ROLE;
    }
}

function format_user_name(string $firstName, string $lastName): string
{
    return strtoupper($firstName) . ' ' . $lastName;
}

$service = new UserService('secret');
echo format_user_name('mario', 'rossi') . PHP_EOL;
print_r($service->findActiveUsers(['a' => 1, 'b' => 2], 5));

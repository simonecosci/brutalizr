<?php
namespace Illuminate\Support\Facades;

class Log
{
    public static function info(string $message): void
    {
        echo "[log] $message\n";
    }
}

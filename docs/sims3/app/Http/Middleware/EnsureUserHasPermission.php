<?php
 
namespace App\Http\Middleware;
 
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;
 
class EnsureUserHasPermission
{
    /**
     * Handle an incoming request.
     *
     * @param  \Closure(\Illuminate\Http\Request): (\Symfony\Component\HttpFoundation\Response)  $next
     */
    public function handle(Request $request, Closure $next, string $roles): Response
    {
        $roles_array = explode('|', $roles);
        foreach ($roles_array as $role) {
            if (in_array($role, $request->user()->permissions)) {
                return $next($request);
            }
        }
        return response('User '.$request->user()->email.' doesnt have the permission '.$roles, 401);
    }
 
}
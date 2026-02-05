# Debugging Guide for Reactive Resume

This guide explains how to debug the Reactive Resume application, including setting breakpoints in both client-side and server-side code.

---

## Quick Start: Step-by-Step Debugging

Follow these steps in order to start debugging:

### Step 1: Start the Development Server

1. **Open a terminal** in VS Code (`` Ctrl+` `` or View → Terminal)
2. **Navigate to the reactive-resume directory** (if not already there):
   ```bash
   cd reactive-resume
   ```
3. **Start the dev server**:
   ```bash
   pnpm run dev
   ```
4. **Wait for the server to start** - You should see output like:
   ```
   VITE v5.x.x  ready in xxx ms
   
   ➜  Local:   http://localhost:3002/
   ```
5. **Verify it's working** - Open `http://localhost:3002` in your browser (don't close the terminal)

### Step 2: Set Breakpoints

1. **Open a file** you want to debug (e.g., `src/components/resume/builder.tsx`)
2. **Find the line** where you want to pause execution
3. **Click in the gutter** (left of the line number) - A red dot appears
4. **Repeat** for any other breakpoints you want

**Example**: Open `src/routes/builder/$resumeId/route.tsx` and set a breakpoint in the component function.

### Step 3: Start Debugging

**Option A: Automatic (Recommended for First Time)**

1. **Press F5** or click the Run and Debug icon in the sidebar (or `Ctrl+Shift+D`)
2. **Select "Debug Client (Chrome)"** from the dropdown at the top
3. **Click the green play button** or press F5 again
4. **Chrome will launch automatically** with the debugger attached
5. **Navigate to** `http://localhost:3002` in the Chrome window that opened
6. **Trigger the code** that hits your breakpoint (click buttons, navigate pages, etc.)
7. **VS Code will pause** at your breakpoint - you can now inspect variables!

**Option B: Manual Chrome Launch (If Option A doesn't work)**

1. **Start Chrome with debugging enabled**:
   
   **Windows (PowerShell)**:
   ```powershell
   & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="$env:TEMP\chrome-debug"
   ```
   
   **Windows (Command Prompt)**:
   ```cmd
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=%TEMP%\chrome-debug
   ```
   
   **macOS**:
   ```bash
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
   ```
   
   **Linux**:
   ```bash
   google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
   ```

2. **In VS Code**: Press F5 → Select "Attach to Chrome" → Press F5 again
3. **Navigate to** `http://localhost:3002` in the Chrome window
4. **Trigger your breakpoint** - VS Code will pause

### Step 4: Debug Your Code

When execution pauses at a breakpoint:

1. **Inspect variables**:
   - Hover over variables in your code to see their values
   - Check the "Variables" panel in the Debug sidebar
   - Add variables to "Watch" for continuous monitoring

2. **Use debug controls**:
   - **Continue (F5)**: Resume execution until next breakpoint
   - **Step Over (F10)**: Execute current line, don't step into functions
   - **Step Into (F11)**: Step into function calls
   - **Step Out (Shift+F11)**: Step out of current function
   - **Restart (Ctrl+Shift+F5)**: Restart debugging session
   - **Stop (Shift+F5)**: Stop debugging

3. **Check the call stack**:
   - See how you got to this point in the "Call Stack" panel
   - Click on different frames to inspect variables in parent scopes

4. **Use the Debug Console**:
   - Type expressions to evaluate them in the current scope
   - Example: Type `user.id` to see the user ID value

### Step 5: Stop Debugging

1. **Press Shift+F5** to stop the debugger
2. **Close Chrome** (if you launched it manually)
3. **Stop the dev server** in the terminal (Ctrl+C)

---

## Visual Guide

```
┌─────────────────────────────────────────────────────────┐
│ STEP 1: Terminal                                        │
│ $ cd reactive-resume                                    │
│ $ pnpm run dev                                          │
│ ✓ Server running on http://localhost:3002              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 2: VS Code Editor                                   │
│ Open: src/components/resume/builder.tsx                 │
│ Click gutter to set breakpoint (red dot appears)         │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 3: VS Code Debug Panel                             │
│ Press F5 → Select "Debug Client (Chrome)" → F5          │
│ Chrome launches automatically                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 4: Chrome Browser                                   │
│ Navigate to http://localhost:3002                       │
│ Click/interact to trigger your breakpoint               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ STEP 5: VS Code Pauses                                  │
│ Execution stops at breakpoint                           │
│ Inspect variables, step through code, etc.              │
└─────────────────────────────────────────────────────────┘
```

---

## Common First-Time Issues

### Issue: "Cannot connect to Chrome"

**Solution**: Make sure Chrome was started with the `--remote-debugging-port=9222` flag. Close Chrome completely and restart it with the command from Step 3 Option B.

### Issue: Breakpoints not hitting

**Solution**: 
1. Make sure the dev server is running (`pnpm run dev`)
2. Make sure you're navigating to `http://localhost:3002` in the Chrome window that VS Code opened
3. Try refreshing the page (F5 in Chrome)
4. Check that your breakpoint is in code that actually runs (not in a comment or type definition)

### Issue: "Port 3002 already in use"

**Solution**: 
1. Stop any other process using port 3002
2. Or change the port in `vite.config.ts` and update `.env` accordingly

---

## Table of Contents

1. [Quick Start: Step-by-Step Debugging](#quick-start-step-by-step-debugging) ← You are here
2. [Prerequisites](#prerequisites)
3. [Debug Configurations](#debug-configurations)
4. [Setting Breakpoints](#setting-breakpoints)
5. [Debugging Client-Side Code](#debugging-client-side-code)
6. [Debugging Server-Side Code](#debugging-server-side-code)
7. [Debugging Full Stack](#debugging-full-stack)
8. [Browser DevTools](#browser-devtools)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Extensions

Ensure you have the following VS Code extensions installed:

- **JavaScript Debugger** (built-in with VS Code)
- **Chrome Debugger** (if using Chrome for debugging)

The recommended extensions from `.vscode/extensions.json` are also helpful:
- Biome (for linting/formatting)
- Tailwind CSS IntelliSense
- i18n Ally

### Verify Setup

1. Ensure the development server can start:
   ```bash
   pnpm run dev
   ```

2. Verify the application loads at `http://localhost:3002`

---

## Debug Configurations

The project includes several debug configurations in `.vscode/launch.json`:

### Available Configurations

1. **Debug Client (Chrome)** - Launches Chrome and attaches debugger to client-side code
2. **Attach to Chrome** - Attaches to an already running Chrome instance with debugging enabled
3. **Debug Server (Node.js)** - Debugs the Vite dev server and SSR code
4. **Attach to Node.js** - Attaches to an already running Node.js process
5. **Debug Full Stack (Chrome + Node)** - Automatically launches both client and server debugging
6. **Debug Client and Server** (Compound) - Runs both client and server debuggers simultaneously

---

## Setting Breakpoints

### How to Set Breakpoints

1. **Open any TypeScript/TSX file** in the `src/` directory
2. **Click in the gutter** (left of line numbers) to set a breakpoint
   - A red dot will appear indicating the breakpoint is set
3. **Right-click the breakpoint** for options:
   - Enable/Disable
   - Edit Breakpoint (conditional breakpoints, logpoints, etc.)
   - Remove Breakpoint

### Types of Breakpoints

- **Regular Breakpoint**: Pauses execution when the line is reached
- **Conditional Breakpoint**: Only pauses when a condition is true
  - Right-click breakpoint → Edit Breakpoint → Enter condition (e.g., `userId === 123`)
- **Logpoint**: Logs a message without pausing
  - Right-click breakpoint → Edit Breakpoint → Logpoint → Enter message (e.g., `User ID: {userId}`)

### Where to Set Breakpoints

#### Client-Side Code (React Components)
- **Components**: `src/components/**/*.tsx`
- **Routes**: `src/routes/**/*.tsx`
- **Hooks**: `src/hooks/**/*.tsx`
- **Utils**: `src/utils/**/*.ts`
- **Lib**: `src/lib/**/*.ts`

Example locations:
```typescript
// src/components/resume/builder.tsx
// src/routes/builder/$resumeId/route.tsx
// src/hooks/use-auth-ready.tsx
// src/lib/api-client.ts
```

#### Server-Side Code (SSR/API Routes)
- **API Routes**: `src/routes/api/**/*.ts`
- **Server Utilities**: `src/integrations/**/*.ts`
- **ORPC Router**: `src/integrations/orpc/router.ts`
- **Server Context**: `src/integrations/orpc/context.ts`

Example locations:
```typescript
// src/routes/api/rpc/route.ts
// src/integrations/orpc/router.ts
// src/integrations/orpc/context.ts
```

---

## Debugging Client-Side Code

### Method 1: Debug Client (Chrome) Configuration

1. **Set breakpoints** in your client-side code (e.g., React components)
2. **Press F5** or go to Run and Debug → Select "Debug Client (Chrome)"
3. **Chrome will launch** automatically with the debugger attached
4. **Navigate to the page** where your breakpoint is located
5. **Execution will pause** at your breakpoint

**Features:**
- Full debugging capabilities (step over, step into, step out)
- Variable inspection
- Call stack navigation
- Watch expressions
- Console evaluation

### Method 2: Attach to Chrome

If you prefer to use your own Chrome instance:

1. **Start Chrome with debugging enabled:**
   ```bash
   # Windows
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%TEMP%\chrome-debug"

   # macOS
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug

   # Linux
   google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-debug
   ```

2. **Navigate to** `http://localhost:3002` in Chrome
3. **In VS Code**: Run and Debug → Select "Attach to Chrome"
4. **Set breakpoints** and debug as normal

### Debugging Tips for Client-Side

- **React Components**: Set breakpoints in component functions, hooks, or event handlers
- **State Changes**: Breakpoints in `useState` setters or `useEffect` callbacks
- **API Calls**: Breakpoints in `src/lib/api-client.ts` or ORPC client code
- **Route Navigation**: Breakpoints in route `loader` or `component` functions

---

## Debugging Server-Side Code

### Method 1: Debug Server (Node.js) Configuration

1. **Set breakpoints** in your server-side code (e.g., API routes, ORPC handlers)
2. **Press F5** or go to Run and Debug → Select "Debug Server (Node.js)"
3. **The dev server will start** with the debugger attached
4. **Make a request** that triggers your server-side code
5. **Execution will pause** at your breakpoint

**Features:**
- Debug SSR code execution
- Inspect server-side variables and context
- Step through ORPC router handlers
- Debug API route handlers

### Method 2: Attach to Node.js

If the dev server is already running:

1. **Start the dev server with inspect flag:**
   ```bash
   NODE_OPTIONS="--inspect" pnpm run dev
   ```

2. **In VS Code**: Run and Debug → Select "Attach to Node.js"
3. **Set breakpoints** in server-side code
4. **Make requests** to trigger breakpoints

### Debugging Tips for Server-Side

- **ORPC Handlers**: Set breakpoints in `src/integrations/orpc/router.ts` handler functions
- **API Routes**: Breakpoints in `src/routes/api/**/*.ts` route handlers
- **Server Context**: Breakpoints in `src/integrations/orpc/context.ts` context functions
- **SSR Code**: Breakpoints in route `loader` functions that run on the server

---

## Debugging Full Stack

### Using Compound Configuration

The "Debug Client and Server" compound configuration allows you to debug both simultaneously:

1. **Set breakpoints** in both client and server code
2. **Press F5** or go to Run and Debug → Select "Debug Client and Server"
3. **Both Chrome and Node.js debuggers** will attach
4. **Navigate the app** and trigger both client and server code
5. **Switch between debuggers** using the dropdown in the Debug panel

### Using Debug Full Stack Configuration

The "Debug Full Stack (Chrome + Node)" configuration automatically:
- Starts the dev server with debugging
- Launches Chrome when the server is ready
- Attaches both debuggers

1. **Set breakpoints** in both client and server code
2. **Press F5** or go to Run and Debug → Select "Debug Full Stack (Chrome + Node)"
3. **Wait for server to start** and Chrome to launch
4. **Debug both sides** simultaneously

---

## Browser DevTools

### Using Chrome DevTools

Even when using VS Code debugging, you can also use Chrome DevTools:

1. **Open Chrome DevTools** (F12)
2. **Use Sources tab** to view and set breakpoints
3. **Use Console tab** to evaluate expressions
4. **Use Network tab** to inspect API calls
5. **Use React DevTools** extension for React component inspection

### Source Maps

The project is configured with source maps enabled. You should see:
- Original TypeScript files in the Sources tab
- Proper file paths matching your `src/` directory structure
- Ability to set breakpoints directly in TypeScript files

If source maps aren't working:
1. Check `vite.config.ts` - source maps should be enabled by default in dev mode
2. Clear browser cache and restart the dev server
3. Verify `tsconfig.json` has `"sourceMap": true` (implicit in Vite)

---

## Troubleshooting

### Breakpoints Not Hitting

**Issue**: Breakpoints are set but execution doesn't pause.

**Solutions:**
1. **Verify source maps are enabled** - Check browser DevTools → Sources → Verify files are mapped correctly
2. **Check breakpoint is in executable code** - Some lines (imports, type definitions) won't hit
3. **Restart debugger** - Stop and restart the debug configuration
4. **Clear browser cache** - Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
5. **Verify file is being executed** - Add a `console.log` to confirm the code runs

### Debugger Not Attaching

**Issue**: VS Code debugger doesn't attach to Chrome/Node.

**Solutions:**
1. **Check port conflicts** - Ensure ports 9222 (Chrome) and 9229 (Node) are available
2. **Verify dev server is running** - The app should be accessible at `http://localhost:3002`
3. **Check extension** - Ensure JavaScript Debugger extension is installed
4. **Restart VS Code** - Sometimes extensions need a restart

### Source Maps Not Working

**Issue**: Can't see TypeScript files, only compiled JavaScript.

**Solutions:**
1. **Verify Vite source maps** - They're enabled by default in dev mode
2. **Check `tsconfig.json`** - Should have proper path mappings
3. **Clear `.vite` cache** - Delete `.vite` folder and restart
4. **Browser DevTools** - Check Sources tab shows TypeScript files

### Server-Side Breakpoints Not Hitting

**Issue**: Server-side breakpoints don't pause execution.

**Solutions:**
1. **Verify NODE_OPTIONS** - Should include `--inspect` flag
2. **Check you're debugging the right process** - Ensure you attached to the correct Node.js process
3. **Verify code is server-side** - Some code only runs on client (check `typeof window !== "undefined"`)
4. **Check route is server-rendered** - Verify the route has a `loader` or server-side logic

### Performance Issues

**Issue**: Debugging is slow or causes performance issues.

**Solutions:**
1. **Disable breakpoints** when not needed - Right-click → Disable All Breakpoints
2. **Use logpoints** instead of breakpoints for frequent code paths
3. **Limit watch expressions** - Too many can slow down debugging
4. **Use conditional breakpoints** - Only pause when needed

---

## Advanced Debugging

### Debugging Specific Scenarios

#### Debugging API Calls
1. Set breakpoint in `src/lib/api-client.ts` request functions
2. Set breakpoint in ORPC client code (`src/integrations/orpc/client.ts`)
3. Set breakpoint in server-side ORPC handlers (`src/integrations/orpc/router.ts`)

#### Debugging Authentication
1. Set breakpoint in `src/utils/jwt.ts` token functions
2. Set breakpoint in `src/integrations/orpc/context.ts` context creation
3. Set breakpoint in route `beforeLoad` functions

#### Debugging State Management
1. Set breakpoint in Zustand store actions
2. Set breakpoint in React Query mutations/queries
3. Set breakpoint in context providers

#### Debugging Route Navigation
1. Set breakpoint in route `loader` functions
2. Set breakpoint in route `component` functions
3. Set breakpoint in `beforeLoad` hooks

### Debug Console

Use the Debug Console in VS Code to:
- **Evaluate expressions** in the current scope
- **Call functions** with different parameters
- **Inspect variables** that aren't in the watch list
- **Modify variable values** (be careful in production!)

### Watch Expressions

Add expressions to watch in the Debug panel:
1. Click "+" in the Watch section
2. Enter an expression (e.g., `user.id`, `resume.title`)
3. Expression is evaluated in the current scope

### Call Stack

Use the Call Stack panel to:
- **Navigate up the call chain** to see how you got to the current breakpoint
- **Jump to different frames** to inspect variables in parent scopes
- **Understand execution flow** through your application

---

## Quick Reference

### Keyboard Shortcuts

| Action | Windows/Linux | macOS |
|--------|---------------|-------|
| Start Debugging | F5 | F5 |
| Stop Debugging | Shift+F5 | Shift+F5 |
| Restart Debugging | Ctrl+Shift+F5 | Cmd+Shift+F5 |
| Continue | F5 | F5 |
| Step Over | F10 | F10 |
| Step Into | F11 | F11 |
| Step Out | Shift+F11 | Shift+F11 |
| Toggle Breakpoint | F9 | F9 |

### Common Debug Commands

- **Continue (F5)**: Resume execution until next breakpoint
- **Step Over (F10)**: Execute current line, don't step into functions
- **Step Into (F11)**: Step into function calls
- **Step Out (Shift+F11)**: Step out of current function
- **Restart (Ctrl+Shift+F5)**: Restart debugging session
- **Stop (Shift+F5)**: Stop debugging

---

## Best Practices

1. **Set breakpoints strategically** - Don't set too many at once
2. **Use conditional breakpoints** for frequently executed code
3. **Use logpoints** for logging without pausing
4. **Clean up breakpoints** after debugging sessions
5. **Use watch expressions** for variables you frequently inspect
6. **Debug in small increments** - Focus on one feature/flow at a time
7. **Use browser DevTools** for network and performance debugging
8. **Test both client and server** code paths when debugging full-stack features

---

## Additional Resources

- [VS Code Debugging Documentation](https://code.visualstudio.com/docs/editor/debugging)
- [Chrome DevTools Documentation](https://developer.chrome.com/docs/devtools/)
- [Node.js Debugging Guide](https://nodejs.org/en/docs/guides/debugging-getting-started/)
- [Vite Debugging Guide](https://vitejs.dev/guide/debugging.html)
- [TanStack Start Documentation](https://tanstack.com/router/latest/docs/framework/react/start/overview)

---

**Happy Debugging! 🐛🔍**

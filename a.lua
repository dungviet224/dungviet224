loadstring(game:HttpGet("https://raw.githubusercontent.com/dungviet224/dungviet224/refs/heads/main/tweentoplayer"))()
local remote = game:GetService("ReplicatedStorage").Modules.Net["RE/ShootGunEvent"]
local player = game.Players.LocalPlayer
local character = player.Character or player.CharacterAdded:Wait()
local rootPart = character:WaitForChild("HumanoidRootPart")
local range = 500 -- Phạm vi kill aura
local canFire = false -- Trạng thái bắn
local firingTime = 3 -- Thời gian bắn liên tục (giây) cho enemy
local shotsPerTarget = 15 -- Số lần bắn mỗi mục tiêu

print("clm")

-- Hàm cập nhật nhân vật khi hồi sinh
local function updateCharacter(newCharacter)
    character = newCharacter
    rootPart = character:WaitForChild("HumanoidRootPart")
end

-- Kết nối sự kiện tái tạo nhân vật
player.CharacterAdded:Connect(updateCharacter)

-- Hàm bắn enemy
local function shootEnemies()
    local inCombat = game:GetService("Players").LocalPlayer.PlayerGui.Main.BottomHUDList.InCombat.Visible
    if inCombat then return end -- Bỏ qua nếu đang trong trạng thái combat

    for _, enemy in pairs(workspace.Enemies:GetChildren()) do
        if enemy:IsA("Model") and enemy:FindFirstChild("HumanoidRootPart") and enemy:FindFirstChild("Humanoid") then
            local enemyRoot = enemy.HumanoidRootPart
            local distance = (rootPart.Position - enemyRoot.Position).Magnitude

            if distance <= range then
                task.spawn(function()
                    for _ = 1, shotsPerTarget do
                        remote:FireServer(rootPart.Position, {enemyRoot})
                        task.wait(0.15) -- Thời gian chờ giữa các phát bắn
                    end
                end)
            end
        end
    end
end

-- Hàm bắn người chơi
local function shootPlayers()
    for _, otherPlayer in pairs(game.Players:GetPlayers()) do
        if otherPlayer ~= player and otherPlayer.Character and otherPlayer.Character:FindFirstChild("HumanoidRootPart") then
            -- Logic bỏ qua bắn nếu người chơi và target đều là Marines
            if player.Team and otherPlayer.Team then
                if player.Team.Name == "Marines" and otherPlayer.Team.Name == "Marines" then
                    continue
                end
            end

            local otherRoot = otherPlayer.Character.HumanoidRootPart
            local distance = (rootPart.Position - otherRoot.Position).Magnitude

            if distance <= range then
                task.spawn(function()
                    for _ = 1, shotsPerTarget do
                        remote:FireServer(rootPart.Position, {otherRoot})
                    end
                end)
            end
        end
    end
end

-- Hàm kiểm tra và bắn mục tiêu
local function shootTarget()
    local inCombat = game:GetService("Players").LocalPlayer.PlayerGui.Main.BottomHUDList.InCombat.Visible

    if inCombat then
        -- Nếu đang trong trạng thái combat, chỉ bắn người chơi
        task.spawn(shootPlayers)
    else
        -- Nếu không trong combat, bắn cả enemy và người chơi
        task.spawn(shootEnemies)
        task.spawn(shootPlayers)
    end
end

-- Lắng nghe sự kiện chuột trái
local userInput = game:GetService("UserInputService")
userInput.InputBegan:Connect(function(input, gameProcessed)
    if gameProcessed then return end -- Bỏ qua nếu sự kiện đã được xử lý
    if input.UserInputType == Enum.UserInputType.MouseButton1 then -- Phát hiện chuột trái
        if not canFire then
            canFire = true
            task.spawn(function()
                shootTarget()
                canFire = false -- Cho phép bắn lại sau khi hoàn thành
            end)
        end
    end
end)
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local player = Players.LocalPlayer
local remotes = ReplicatedStorage.Remotes.CommE

local toggleSoru = false

local function getClosestPlayer()
    local closestPlayer = nil
    local shortestDistance = 300 -- 300 meters (studs)

    for _, otherPlayer in ipairs(Players:GetPlayers()) do
        if otherPlayer ~= player and otherPlayer.Character and otherPlayer.Character:FindFirstChild("HumanoidRootPart") then
            local distance = (otherPlayer.Character.HumanoidRootPart.Position - player.Character.HumanoidRootPart.Position).Magnitude
            if distance < shortestDistance then
                closestPlayer = otherPlayer
                shortestDistance = distance
            end
        end
    end

    return closestPlayer
end

local function performSoru()
    local character = player.Character
    if not character or not character:FindFirstChild("HumanoidRootPart") then return end

    local closestPlayer = getClosestPlayer()
    if closestPlayer and closestPlayer.Character and closestPlayer.Character:FindFirstChild("HumanoidRootPart") then
        local playerCFrame = character.HumanoidRootPart.CFrame
        local targetCFrame = closestPlayer.Character.HumanoidRootPart.CFrame

        remotes:FireServer("Soru", playerCFrame, targetCFrame, tick(), math.random(1000000, 9999999))
    end
end

-- Toggle logic
local UserInputService = game:GetService("UserInputService")
UserInputService.InputBegan:Connect(function(input, isProcessed)
    if isProcessed then return end
    if input.KeyCode == Enum.KeyCode.F then
        toggleSoru = not toggleSoru
        print(toggleSoru)
    end
end)

-- Continuously perform Soru when toggled
RunService.RenderStepped:Connect(function()
    if toggleSoru then
        performSoru()
        task.wait(0.01) -- Adjust delay as needed
    end
end)
print("A")

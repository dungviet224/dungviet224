local remote = game:GetService("ReplicatedStorage").Modules.Net["RE/ShootGunEvent"]
local player = game.Players.LocalPlayer
local character = player.Character or player.CharacterAdded:Wait()
local rootPart = character:WaitForChild("HumanoidRootPart")
local range = 500 -- Phạm vi kill aura
local canFire = false -- Trạng thái bắn
local firingTime = 2 -- Thời gian bắn liên tục (giây) cho enemy
local shotsPerTarget = 15 -- Số lần bắn mỗi người chơi

print("clm")

-- Hàm cập nhật nhân vật khi hồi sinh
local function updateCharacter(newCharacter)
    character = newCharacter
    rootPart = character:WaitForChild("HumanoidRootPart")
end

-- Kết nối sự kiện tái tạo nhân vật
player.CharacterAdded:Connect(updateCharacter)
-- Thêm target là tất cả con SeaBeast trong workspace
-- Thêm target từ workspace.Enemies.PirateGrandBrigade.Body:GetChildren()
local function shootEnemies()
    local inCombat = game:GetService("Players").LocalPlayer.PlayerGui.Main.BottomHUDList.InCombat.Visible
    if inCombat then return end -- Bỏ qua nếu đang trong trạng thái combat

    local endTime = tick() + firingTime
    while tick() < endTime do
        -- Bắn Enemy
        for _, enemy in pairs(workspace.Enemies:GetChildren()) do
            if enemy:IsA("Model") and enemy:FindFirstChild("HumanoidRootPart") and enemy:FindFirstChild("Humanoid") then
                local enemyRoot = enemy.HumanoidRootPart
                local distance = (rootPart.Position - enemyRoot.Position).Magnitude

                if distance <= range then
                    remote:FireServer(rootPart.Position, {enemyRoot})
                end
            end
        end

        -- Bắn SeaBeasts
        for _, seaBeast in pairs(workspace.SeaBeasts:GetChildren()) do
            if seaBeast:IsA("Model") and seaBeast:FindFirstChild("HumanoidRootPart") then
                local seaBeastRoot = seaBeast.HumanoidRootPart
                local distance = (rootPart.Position - seaBeastRoot.Position).Magnitude

                if distance <= range then
                    remote:FireServer(rootPart.Position, {seaBeastRoot})
                end
            end
        end

        -- Bắn PirateGrandBrigade Body
        local pirateGrandBrigade = workspace.Enemies:FindFirstChild("PirateGrandBrigade") or workspace.Enemies:FindFirstChild("PirateBrigade") or workspace.Enemies:FindFirstChild("FishBoat")
        if pirateGrandBrigade and pirateGrandBrigade:FindFirstChild("Body") then
            for _, part in pairs(pirateGrandBrigade.Body:GetChildren()) do
                if part:IsA("BasePart") then
                    local distance = (rootPart.Position - part.Position).Magnitude

                    if distance <= range then
                        remote:FireServer(rootPart.Position, {part})
                    end
                end
            end
        end
        task.wait(0.05) -- Đợi trước khi tiếp tục bắn
    end
end

-- Hàm bắn người chơi
local function shootPlayers()
    for _, otherPlayer in pairs(game.Players:GetPlayers()) do
        if otherPlayer.Name == "AFAmMNoaff" then
            continue -- Bỏ qua người chơi có tên "AFAmMNoaff"
        end

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
    if input.UserInputType == Enum.UserInputType.MouseButton1 or input.UserInputType == Enum.UserInputType.Touch then -- Phát hiện chuột trái
        if not canFire then
            canFire = true
            task.spawn(function()
                shootTarget()
                canFire = false -- Cho phép bắn lại sau khi hoàn thành
            end)
        end
    end
end)

with (instance_create(x, y, obj_rock))
{
	if (alarm[1] > 10)
	{
		instance_destroy();
	}
	else
	{
		switch (keyboard_key)
		{
		case vk_shift:
			game_save("saving");
		case vk_up:
			game_restart();
		default:
			break;
		}
	}
}
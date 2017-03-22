with (instance_create_layer(x, y, "instance_layer", obj_rock))
{
	if (alarm[10] > 10)
	{
		instance_destroy();
	}
	else
	{
		
		switch (keyboard_key)
		{
		case vk_shift:
			game_save("Save.dat");
		case vk_up:
			game_restart();
		default:
			break;
		}
	}
}
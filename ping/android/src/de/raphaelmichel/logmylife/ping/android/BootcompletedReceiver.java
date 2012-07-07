package de.raphaelmichel.logmylife.ping.android;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;

public class BootcompletedReceiver extends BroadcastReceiver {

	@Override
	public void onReceive(Context context, Intent intent) {
		Intent i = new Intent(context, AlarmReceiver.class);
		PendingIntent sender = PendingIntent.getBroadcast(context, AlarmReceiver.requestCode, i, PendingIntent.FLAG_UPDATE_CURRENT);
		 
		SharedPreferences sp = PreferenceManager.getDefaultSharedPreferences(context);
  	  	if(sp.getBoolean("service_active", true)){
			// Get the AlarmManager service
			AlarmManager am = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
			am.set(AlarmManager.RTC_WAKEUP, System.currentTimeMillis() + 10000, sender);
  	  	}
	}
}
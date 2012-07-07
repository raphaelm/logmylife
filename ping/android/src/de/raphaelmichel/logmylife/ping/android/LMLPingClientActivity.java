package de.raphaelmichel.logmylife.ping.android;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.preference.Preference;
import android.preference.PreferenceActivity;
import android.preference.PreferenceManager;
import android.util.Log;

public class LMLPingClientActivity extends PreferenceActivity {
	protected SharedPreferences sp;
	protected SharedPreferences.OnSharedPreferenceChangeListener spChanged;
	
    @Override
	protected void onRestart() {
		super.onRestart();       
        Preference lastping = getPreferenceScreen().findPreference("last_ping");
        lastping.setSummary(sp.getString("last_ping", "Unknown"));
	}

	@Override
	protected void onResume() {
		super.onResume();       
        Preference lastping = getPreferenceScreen().findPreference("last_ping");
        lastping.setSummary(sp.getString("last_ping", "Unknown"));
	}

	/** Called when the activity is first created. */
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        addPreferencesFromResource(R.xml.preferences);

        sp = PreferenceManager.getDefaultSharedPreferences(getApplicationContext());
        
        final Preference lastping = getPreferenceScreen().findPreference("last_ping");
        lastping.setSummary(sp.getString("last_ping", "Unknown"));
		
        final Intent i = new Intent(getApplicationContext(), AlarmReceiver.class);
        final PendingIntent sender = PendingIntent.getBroadcast(getApplicationContext(), AlarmReceiver.requestCode, i, PendingIntent.FLAG_UPDATE_CURRENT);

        final AlarmManager am = (AlarmManager) getSystemService(Context.ALARM_SERVICE);
		
    	spChanged = new SharedPreferences.OnSharedPreferenceChangeListener() {
			@Override
			public void onSharedPreferenceChanged(
					SharedPreferences sharedPreferences, String key) {
				if(!key.equals("service_active"))
					return;
				
	      	  	if(!sharedPreferences.getBoolean("service_active", false)){
	      	  		Log.i("start", "cancel");
	    			am.cancel(sender);
	      	  	}else{
	      	  		Log.i("start", "start");
	    			am.cancel(sender);
	    			am.set(AlarmManager.RTC_WAKEUP, System.currentTimeMillis() + 10000, sender);
	    		}
			}
    	};
    	sp.registerOnSharedPreferenceChangeListener(spChanged);
	  	
  	  	if(!sp.getBoolean("service_active", false)){
  	  		Log.i("start", "cancel");
			am.cancel(sender);
  	  	}else{
  	  		Log.i("start", "start");
			am.set(AlarmManager.RTC_WAKEUP, System.currentTimeMillis() + 10000, sender);
  	  	}
    }
}
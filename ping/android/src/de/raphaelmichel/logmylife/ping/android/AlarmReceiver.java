package de.raphaelmichel.logmylife.ping.android;

import java.text.DateFormat;
import java.util.Date;

import org.apache.http.HttpResponse;
import org.apache.http.StatusLine;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.impl.client.DefaultHttpClient;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.ConnectivityManager;
import android.preference.PreferenceManager;
import android.net.NetworkInfo;
import android.util.Log;

public class AlarmReceiver extends BroadcastReceiver {
	public static int requestCode = 192839;
	@Override
	public void onReceive(Context context, Intent intent) {
		Log.i("fired", "fired");
		
		Intent i = new Intent(context, AlarmReceiver.class);
		PendingIntent sender = PendingIntent.getBroadcast(context, AlarmReceiver.requestCode, i, PendingIntent.FLAG_UPDATE_CURRENT);
		
		SharedPreferences sp = PreferenceManager.getDefaultSharedPreferences(context.getApplicationContext());
		AlarmManager am = (AlarmManager) context.getSystemService(Context.ALARM_SERVICE);
		
  	  	if(!sp.getBoolean("service_active", false)){
			am.cancel(sender);
  	  	}
  	  	
  	  	ConnectivityManager conMgr =  (ConnectivityManager)context.getSystemService(Context.CONNECTIVITY_SERVICE);

		if ( conMgr.getNetworkInfo(0).getState() == NetworkInfo.State.CONNECTED 
		    ||  conMgr.getNetworkInfo(1).getState() == NetworkInfo.State.CONNECTING  ) {
		
		}
		else if ( conMgr.getNetworkInfo(0).getState() == NetworkInfo.State.DISCONNECTED 
		    ||  conMgr.getNetworkInfo(1).getState() == NetworkInfo.State.DISCONNECTED) {
		    Log.i("alarm", "no network");
			return; // not online		
		}
		HttpClient client = new DefaultHttpClient();
		HttpGet httpGet = new HttpGet(
				sp.getString("ping_url", "http://www.raphaelmichel.de/stats/pingserver/recieve.php")+
				"?key="+sp.getString("ping_key", "")+
				"&device="+sp.getString("ping_device", ""));
		try {
			HttpResponse response = client.execute(httpGet);
			StatusLine statusLine = response.getStatusLine();
			int statusCode = statusLine.getStatusCode();
			if (statusCode == 200) {
				SharedPreferences.Editor spe = sp.edit();
				spe.putString("last_ping", DateFormat.getDateTimeInstance().format(new Date()));
				spe.commit();
			}else{
				Log.i("alarm", ""+statusCode);
			}
		}catch(Exception e){
			e.printStackTrace();
		}
	}

}

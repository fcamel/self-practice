package org.fcamel.remotecontroller;

import java.io.BufferedWriter;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.logging.Logger;

import android.net.DhcpInfo;
import android.net.wifi.WifiManager;
import android.os.AsyncTask;
import android.os.Bundle;
import android.app.Activity;
import android.content.Context;
import android.content.pm.PackageManager;
import android.util.Log;
import android.view.Menu;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Button;
import android.widget.SeekBar;
import android.widget.TextView;

public class MainActivity extends Activity implements
		SeekBar.OnSeekBarChangeListener, OnClickListener {
	static MainActivity sActivity = null;
	static final int MAX_VOLUME = 64 * 1000;
	static final int SERVER_PORT = 6100;

	String sServerIp = "";

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);

		sActivity = this;

		setContentView(R.layout.activity_main);

		Button scanIp = (Button) findViewById(R.id.scanIpButton);
		scanIp.setOnClickListener(this);

		SeekBar seekBar = (SeekBar) findViewById(R.id.volumeSeekBar);
		seekBar.setOnSeekBarChangeListener(this);
		seekBar.setMax(MAX_VOLUME);
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		// Inflate the menu; this adds items to the action bar if it is present.
		getMenuInflater().inflate(R.menu.main, menu);
		return true;
	}

	@Override
	public void onProgressChanged(SeekBar bar, int progress, boolean fromUser) {
	}

	private void SetRemoteVolume(int volume) {
		new SetVolumeTask().execute(volume);
	}

	@Override
	public void onStartTrackingTouch(SeekBar arg0) {
		TextView view = (TextView) findViewById(R.id.volumeMessage);
		view.setText("");
	}

	@Override
	public void onStopTrackingTouch(SeekBar bar) {
		int volume = bar.getProgress();
		Log.d("mytag", "stop: " + Integer.toString(volume));
		SetRemoteVolume(volume);
	}

	@Override
	public void onClick(View view) {
		scanIp();
	}

	void scanIp() {
		TextView view = (TextView) MainActivity.sActivity
				.findViewById(R.id.scanIpMessage);
		view.setText("");
		new ScanIpTask().execute();
	}
}

class SetVolumeTask extends AsyncTask<Integer, Void, Boolean> {
	private Socket socket = null;

	@Override
	protected Boolean doInBackground(Integer... volumes) {
		if (MainActivity.sActivity.sServerIp == null) {
			return false;
		}
		int volume = volumes[0].intValue();
		InetAddress serverAddr;
		try {
			serverAddr = InetAddress
					.getByName(MainActivity.sActivity.sServerIp);
		} catch (UnknownHostException e) {
			e.printStackTrace();
			return false;
		}

		try {
			socket = new Socket();
			// Set a short timeout since we are in LAN.
			socket.connect(new InetSocketAddress(serverAddr,
					MainActivity.SERVER_PORT), 100);
		} catch (IOException e) {
			e.printStackTrace();
			return false;
		}

		try {
			PrintWriter out = new PrintWriter(new BufferedWriter(
					new OutputStreamWriter(socket.getOutputStream())), true);
			out.println(volume);
		} catch (IOException e) {
			e.printStackTrace();
			return false;
		}
		try {
			socket.close();
		} catch (IOException e) {
			e.printStackTrace();
		}
		return true;
	}

	@Override
	protected void onPostExecute(Boolean result) {
		String message = result ? "Done" : "Failed";
		TextView view = (TextView) MainActivity.sActivity
				.findViewById(R.id.volumeMessage);
		view.setText(message);
	}
}

class ScanIpTask extends AsyncTask<Void, Void, String> {

	@Override
	protected String doInBackground(Void... arg0) {
		// TODO Show "working progress" animation.
		// Get current IP
		WifiManager wifiMananger = (WifiManager) MainActivity.sActivity
				.getSystemService(Context.WIFI_SERVICE);
		DhcpInfo info = wifiMananger.getDhcpInfo();
		if (info.netmask != ((1 << 24) - 1)) {
			return "Netmask is not 24bits. Cannot find the server IP automatically.";
		}
		Log.d("mytag", "localIp: " + String.valueOf(info.ipAddress)
				+ ", mask: " + String.valueOf(info.netmask) + ", gateway: "
				+ String.valueOf(info.gateway));

		// Scan IP in LAN
		String network = ToNetworkDomainString(info.ipAddress);
		for (int i = 1; i < 255; i++) {
			String ip = network + Integer.toString(i);
			try {
				InetAddress serverAddr = InetAddress.getByName(ip);
				Socket socket = new Socket();
				// Set a short timeout since we are in LAN.
				socket.connect(new InetSocketAddress(serverAddr,
						MainActivity.SERVER_PORT), 100);
				socket.close();
				// Successfully to connect the server. Record it.
				MainActivity.sActivity.sServerIp = ip;
				return "Found the server IP: " + ip;
			} catch (UnknownHostException e) {
				e.printStackTrace();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}
		return "Cannot find any server.";
	}

	// Only work when netmask uses 24 bits.
	private String ToNetworkDomainString(int ip) {
		// The IP is in reversed order.
		String result = (ip & 0xFF) + "." + ((ip >> 8) & 0xFF) + "."
				+ ((ip >> 16) & 0xFF) + ".";
		Log.d("mytag", "Network domain: " + result);
		return result;
	}

	@Override
	protected void onPostExecute(String result) {
		TextView view = (TextView) MainActivity.sActivity
				.findViewById(R.id.scanIpMessage);
		view.setText(result);
	}

}

<?php

namespace App\Mail;

use App\Models\Sample;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class SiteOpenOrSelection extends Mailable
{
    use Queueable, SerializesModels;

    /**
     * Create a new message instance.
     */
    public function __construct(public Sample $sample,)
    {
        //
    }

    /**
     * Get the message envelope.
     */
    public function envelope(): Envelope
    {  
        if ($this->sample->type=="Site_Opening")
        {
            return new Envelope(
                subject: 'New Sample For Site Opening '.$this->sample->site,
            );
        } 
        if ($this->sample->type=="Site_Selection")
        {
            return new Envelope(
                subject: 'New Sample For Site Selection',
            );
        }
        if ($this->sample->type=="Site_Intervention")
        {
            return new Envelope(
                subject: 'New Sample For Site Intervention',
            );
        }
        
    }

    /**
     * Get the message content definition.
     */
    public function content(): Content
    {
        if ($this->sample->type=="Site_Opening")
        {
            return new Content(
                markdown: 'emails.siteOpenAndSelection.alertSiteOpen',
            );
        } 
        if ($this->sample->type=="Site_Selection")
        {
            return new Content(
                markdown: 'emails.siteOpenAndSelection.alertSiteSelection',
            );
        }
        if ($this->sample->type=="Site_Intervention")
        {
            return new Content(
                markdown: 'emails.siteOpenAndSelection.alertSiteIntervention',
            );
        }
    }

    /**
     * Get the attachments for the message.
     *
     * @return array<int, \Illuminate\Mail\Mailables\Attachment>
     */
    public function attachments(): array
    {
        return [];
    }
}
